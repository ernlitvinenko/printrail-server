import enum
from datetime import date

from sqlalchemy import String, ForeignKey, func, types, Enum, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.database.base import Base


class GenderType(enum.Enum):
    MALE = 1
    FEMALE = 2


class ContactInfoType(enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"


class JobPosition(Base):
    __tablename__ = "job_position"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    employees: Mapped[list['Employee']] = relationship(back_populates="position")

employee__contact_info_cross = Table("employee__contact_info_cross",
                                     Base.metadata,
                                     Column("employee_id", Integer, ForeignKey("employee.id"), primary_key=True),
                                     Column("contact_info_id", Integer, ForeignKey("contact_info.id"), primary_key=True),
                                     )

class Employee(Base):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="ФИО сотрудника")
    subsection: Mapped[str] = mapped_column(String(32), nullable=False, default="Основное", comment="Подразделение")
    position_id: Mapped[int] = mapped_column(ForeignKey("job_position.id"),
                                             comment="Идентификатор занимаемой должности", nullable=False)
    position: Mapped[JobPosition] = relationship(back_populates="employees")
    date_approved: Mapped[date] = mapped_column(nullable=False, comment="Дата принятия")
    date_fired: Mapped[date] = mapped_column(nullable=True, comment="Дата увольнения")
    date_of_birth: Mapped[date] = mapped_column(nullable=False, comment="Дата рождения")
    gender: Mapped[GenderType] = mapped_column(Enum(GenderType, name="gender_type", native_enum=True), nullable=False, comment="Пол")

    contacts: Mapped[list['ContactInfo']] = relationship(secondary=employee__contact_info_cross)


class ContactInfo(Base):
    __tablename__ = "contact_info"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ContactInfoType] = mapped_column(Enum(ContactInfoType, name="contact_type", native_enum=True), nullable=False)
    data: Mapped[str] = mapped_column(String(256), nullable=False)


