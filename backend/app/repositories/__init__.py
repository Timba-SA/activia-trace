from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.auth_repository import (
    RecoveryTokenRepository,
    SesionRepository,
    UsuarioRepository,
)
from app.repositories.aviso_repository import (
    AcknowledgmentRepository,
    AvisoRepository,
)
from app.repositories.base import BaseRepository
from app.repositories.coloquio_repository import (
    ConvocatoriaAlumnoRepository,
    EvaluacionRepository,
    ReservaEvaluacionRepository,
    ResultadoEvaluacionRepository,
    TurnoDisponibleRepository,
)
from app.repositories.encuentro_repository import (
    InstanciaEncuentroRepository,
    SlotEncuentroRepository,
)
from app.repositories.guardia_repository import GuardiaRepository
from app.repositories.mensaje_repository import MensajeRepository
from app.repositories.role_repository import RoleRepository, UsuarioRoleRepository
from app.repositories.tarea_repository import (
    ComentarioTareaRepository,
    TareaRepository,
)
from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.repositories.tenant import TenantRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.repositories.materia_grupo_plus_repository import MateriaGrupoPlusRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.factura_repository import FacturaRepository

__all__ = [
    "AcknowledgmentRepository",
    "AuditLogRepository",
    "AvisoRepository",
    "BaseRepository",
    "ComentarioTareaRepository",
    "ConvocatoriaAlumnoRepository",
    "EvaluacionRepository",
    "FechaAcademicaRepository",
    "GuardiaRepository",
    "MensajeRepository",
    "InstanciaEncuentroRepository",
    "ProgramaMateriaRepository",
    "RecoveryTokenRepository",
    "ReservaEvaluacionRepository",
    "ResultadoEvaluacionRepository",
    "RoleRepository",
    "SesionRepository",
    "SlotEncuentroRepository",
    "TareaRepository",
    "TenantRepository",
    "TurnoDisponibleRepository",
    "UsuarioRepository",
    "UsuarioRoleRepository",
    "SalarioBaseRepository",
    "SalarioPlusRepository",
    "MateriaGrupoPlusRepository",
    "LiquidacionRepository",
    "FacturaRepository",
]
