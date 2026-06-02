## ADDED Requirements

### Requirement: Cifrado AES-256-GCM para atributos PII

El sistema SHALL proveer dos funciones en `core/security.py`: `encrypt_value(plaintext: str) -> str` y `decrypt_value(ciphertext: str) -> str`. El cifrado SHALL usar AES-256 en modo GCM (autenticado). La clave SHALL ser `ENCRYPTION_KEY` de Settings (exactamente 32 caracteres, codificada a UTF-8 bytes). Cada operación de cifrado SHALL generar un nonce aleatorio de 12 bytes. El output SHALL ser base64 (nonce + ciphertext + tag). Si el descifrado falla (tag inválido o clave incorrecta), SHALL lanzar `EncryptionError`.

#### Scenario: Cifrado y descifrado round-trip exitoso

- **WHEN** se cifra un texto plano con `encrypt_value` y luego se descifra el resultado con `decrypt_value`
- **THEN** el texto descifrado coincide exactamente con el texto plano original

#### Scenario: Cifrados distintos para mismo texto plano

- **WHEN** se cifra el mismo texto plano dos veces con diferentes nonces
- **THEN** los ciphertexts resultantes son diferentes (nonce aleatorio garantiza diferenciación)

#### Scenario: Descifrado con clave incorrecta falla

- **WHEN** se intenta descifrar un ciphertext con una clave diferente a la usada para cifrar
- **THEN** se lanza `EncryptionError`

#### Scenario: Descifrado de base64 inválido falla

- **WHEN** se pasa un string que no es base64 válido a `decrypt_value`
- **THEN** se lanza `EncryptionError`

#### Scenario: Cifrado de string vacío

- **WHEN** se cifra un string vacío con `encrypt_value("")`
- **THEN** la operación es exitosa y el round-trip devuelve string vacío

### Requirement: La clave de cifrado se valida en Settings

La variable `ENCRYPTION_KEY` SHALL ser validada por el schema de Settings para garantizar exactamente 32 caracteres. Si no cumple la longitud, la app NO SHALL iniciar.

#### Scenario: ENCRYPTION_KEY de longitud inválida

- **WHEN** `ENCRYPTION_KEY` tiene menos o más de 32 caracteres
- **THEN** la validación de Settings falla y la aplicación no arranca
