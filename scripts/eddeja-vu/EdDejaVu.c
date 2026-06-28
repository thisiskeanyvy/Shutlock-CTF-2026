// gcc -o EdDejaVu chall.c -lsodium -O2
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sodium.h>

#define KEY_SIZE 32
#define SIG_SIZE 64
#define SIGN_LIMIT 128

static uint8_t g_seed[KEY_SIZE];
static uint8_t g_privkey[crypto_sign_SECRETKEYBYTES];
static uint8_t g_pubkey[KEY_SIZE];

static void print_hex(const char *pred, const uint8_t *data, size_t n) {
    printf("%s", pred);
    for (size_t i = 0; i < n; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

static int hex_to_bytes(const char *hex, uint8_t *bytes, size_t n) {
    if (strlen(hex) != n*2)
        return -1;
    for (size_t i = 0; i < n; i++) {
        if (sscanf(hex + 2*i, "%2hhx", &bytes[i]) != 1)
            return -1;
    }
    return 0;
}

static void get_flag(void) {
    FILE *f = fopen("flag.txt", "r");
    if (!f) {
        printf("Are you sure flag.txt exist?\n");
        return;
    }
    char flag[256];
    if (fgets(flag, sizeof(flag), f))
        printf("\nCorrect! %s\n", flag);
    fclose(f);
}

static void generate_keypair(void) {
    if (sodium_init() < 0)
        exit(1);
    randombytes_buf(g_seed, sizeof(g_seed));
    if (crypto_sign_seed_keypair(g_pubkey, g_privkey, g_seed) != 0)
        exit(1);

    printf("===========================\n");
    printf("         EdDéjàVu\n");
    printf(" Un petit air de déjà vu...\n");
    printf("============================\n");
    print_hex("Public Key: ", g_pubkey, KEY_SIZE);
}

static void clamp(uint8_t scalar[KEY_SIZE]) {
    scalar[0] &= 248;
    scalar[31] &= 127;
    scalar[31] |= 64;
}

static void sign_message(const uint8_t *input, size_t input_len, uint8_t signature[SIG_SIZE]) {
    crypto_hash_sha512_state state;
    size_t len = (input_len > SIGN_LIMIT) ? SIGN_LIMIT : input_len;

    unsigned long sum = 0;
    for(size_t i=0; i < input_len; i++)
        sum += input[i];

    // k_scalar = H(privkey || M)
    uint8_t hash[64];
    crypto_hash_sha512_init(&state);
    crypto_hash_sha512_update(&state, g_privkey, KEY_SIZE);
    crypto_hash_sha512_update(&state, input, len);
    crypto_hash_sha512_final(&state, hash);
    uint8_t k_scalar[KEY_SIZE];
    memcpy(k_scalar, hash, KEY_SIZE);
    if (sum % 2) clamp(k_scalar);

    // k = k_scalar % L
    uint8_t k[KEY_SIZE];
    uint8_t tmp[64] = {0};
    memcpy(tmp, k_scalar, KEY_SIZE);
    crypto_core_ed25519_scalar_reduce(k, tmp);

    // R = k * G
    uint8_t R[KEY_SIZE];
    crypto_scalarmult_ed25519_base_noclamp(R, k);

    // e = H(R || A || M)
    uint8_t e_hash[64];
    crypto_hash_sha512_init(&state);
    crypto_hash_sha512_update(&state, R, KEY_SIZE);
    crypto_hash_sha512_update(&state, g_pubkey, KEY_SIZE);
    crypto_hash_sha512_update(&state, input, len);
    crypto_hash_sha512_final(&state, e_hash);
    uint8_t e[KEY_SIZE];
    crypto_core_ed25519_scalar_reduce(e, e_hash);

    // S = k + e*x
    uint8_t az[64];
    crypto_hash_sha512(az, g_privkey, 32);
    clamp(az);
    uint8_t priv_reduced[KEY_SIZE];
    memcpy(tmp, az, KEY_SIZE);
    crypto_core_ed25519_scalar_reduce(priv_reduced, tmp);
    uint8_t e_times_priv[KEY_SIZE];
    crypto_core_ed25519_scalar_mul(e_times_priv, e, priv_reduced);
    uint8_t s[KEY_SIZE];
    crypto_core_ed25519_scalar_add(s, k, e_times_priv);

    // signature = (R, S)
    memcpy(signature, R, KEY_SIZE);
    memcpy(signature + KEY_SIZE, s, KEY_SIZE);
}

static void sign(void) {
    char input[512];
    printf("Message (hex): ");
    if (!fgets(input, sizeof(input), stdin))
        return;

    input[strcspn(input, "\n")] = 0;

    size_t hex_len = strlen(input);
    size_t bin_len = hex_len / 2;
    uint8_t *buffer = malloc(bin_len);

    if (hex_to_bytes(input, buffer, bin_len) != 0) {
        printf("Invalid hex\n");
        free(buffer);
        return;
    }

    uint8_t signature[SIG_SIZE];
    sign_message(buffer, bin_len, signature);
    print_hex("Signature: ", signature, SIG_SIZE);
    printf("\n");
    free(buffer);
}

static void submit(void) {
    char input[256];
    printf("Enter private key (hex): ");
    if (!fgets(input, sizeof(input), stdin))
        return;
    input[strcspn(input, "\n")] = 0;

    uint8_t submitted_key[KEY_SIZE];
    if (hex_to_bytes(input, submitted_key, KEY_SIZE) != 0)
        return;
    uint8_t az[64];
    crypto_hash_sha512(az, g_privkey, 32);
    clamp(az);

    uint8_t correct_scalar[KEY_SIZE];
    uint8_t tmp[64] = {0};
    memcpy(tmp, az, KEY_SIZE);
    crypto_core_ed25519_scalar_reduce(correct_scalar, tmp);
    if (memcmp(submitted_key, correct_scalar, KEY_SIZE) == 0)
        get_flag();
    else
        printf("Wrong key!\n");
    exit(0);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    generate_keypair();

    while (1) {
        printf("1: Sign\n2: Solve\n> ");
        char buf[16];
        if (!fgets(buf, sizeof(buf), stdin))
            break;
        if (atoi(buf) == 1)
            sign();
        else if (atoi(buf) == 2)
            submit();
    }
    return 0;
}
