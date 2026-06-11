"""Test JWT token creation and decoding."""
import asyncio
import uuid
from app.core.security import create_access_token, decode_token
from app.core.database import get_factory
from sqlalchemy import text


async def debug():
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000100")
    tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    # Create token like login does
    user_data = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": [],
    }
    token = create_access_token(user_data)
    print(f"Token created: {token[:60]}...")

    # Decode
    try:
        payload = decode_token(token)
        print(f"Decoded OK: sub={payload.get('sub')}, tenant_id={payload.get('tenant_id')}")
    except Exception as e:
        print(f"Decode FAILED: {e}")

    # Test full login flow via the auth service
    from app.models.usuario import Usuario
    from app.repositories.auth_repository import UsuarioRepository
    from app.services.auth_service import AuthService
    from app.repositories.auth_repository import SesionRepository, RecoveryTokenRepository

    factory = get_factory()
    async with factory() as session:
        # Check if user exists
        result = await session.execute(
            text("SELECT id, email, tenant_id FROM usuario WHERE email = 'admin@activia-trace.com'")
        )
        user_row = result.first()
        if user_row:
            print(f"User found: {user_row}")
        else:
            print("User NOT found!")
            return

        # Try the auth service login
        user_repo = UsuarioRepository(session, tenant_id)
        sesion_repo = SesionRepository(session)
        recovery_repo = RecoveryTokenRepository(session)
        service = AuthService(user_repo, sesion_repo, recovery_repo)

        result = await service.login("admin@activia-trace.com", "admin123")
        if "error" in result:
            print(f"Login failed: {result['error']}")
        else:
            print(f"Login OK! Token: {result['access_token'][:60]}...")
            # Decode the token from login
            token2 = result["access_token"]
            try:
                payload = decode_token(token2)
                print(f"Login token decoded OK: sub={payload.get('sub')}")
            except Exception as e:
                print(f"Login token decode FAILED: {e}")


asyncio.run(debug())
