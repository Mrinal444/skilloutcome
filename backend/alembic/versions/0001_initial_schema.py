"""Create the complete SkillOutcome schema."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    enums = [
        sa.Enum("ADMIN", "TRAINEE", "PROVIDER", "EMPLOYER", name="userrole"),
        sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="skilllevel"),
        sa.Enum("ONGOING", "COMPLETED", "DROPPED", name="enrollmentstatus"),
        sa.Enum("EMPLOYED", "RESIGNED", "TERMINATED", name="employmentstatus"),
        sa.Enum("DAY_30", "DAY_90", "DAY_180", name="followuptype"),
        sa.Enum("EMPLOYED", "UNEMPLOYED", "SELF_EMPLOYED", "FURTHER_TRAINING", name="followupstatus"),
    ]
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for item in enums:
            item.create(bind, checkfirst=True)
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.Enum("ADMIN", "TRAINEE", "PROVIDER", "EMPLOYER", name="userrole"), nullable=False), sa.Column("created_at", sa.DateTime()))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("skills", sa.Column("skill_id", sa.Integer(), primary_key=True), sa.Column("skill_name", sa.String(100), nullable=False), sa.Column("category", sa.String(100)), sa.UniqueConstraint("skill_name"))
    op.create_table("employers", sa.Column("employer_id", sa.Integer(), primary_key=True), sa.Column("company_name", sa.String(200), nullable=False), sa.Column("industry", sa.String(100)), sa.Column("location", sa.String(100)), sa.Column("verification_status", sa.Boolean()), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.create_index("ix_employers_user_id", "employers", ["user_id"])
    op.create_table("trainees", sa.Column("trainee_id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("education", sa.String(100)), sa.Column("location", sa.String(100)), sa.Column("experience", sa.Integer()), sa.UniqueConstraint("user_id"))
    op.create_table("training_programs", sa.Column("program_id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("provider", sa.String(200), nullable=False), sa.Column("duration", sa.String(50)), sa.Column("category", sa.String(100)), sa.Column("provider_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.create_index("ix_training_programs_provider_user_id", "training_programs", ["provider_user_id"])
    op.create_table("trainee_skills", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("trainee_id", sa.Integer(), sa.ForeignKey("trainees.trainee_id"), nullable=False), sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.skill_id"), nullable=False), sa.Column("level", sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="skilllevel")), sa.UniqueConstraint("trainee_id", "skill_id", name="uq_trainee_skill"))
    op.create_index("ix_trainee_skills_trainee_id", "trainee_skills", ["trainee_id"])
    op.create_table("training_enrollments", sa.Column("enrollment_id", sa.Integer(), primary_key=True), sa.Column("trainee_id", sa.Integer(), sa.ForeignKey("trainees.trainee_id"), nullable=False), sa.Column("program_id", sa.Integer(), sa.ForeignKey("training_programs.program_id"), nullable=False), sa.Column("start_date", sa.DateTime()), sa.Column("completion_date", sa.DateTime()), sa.Column("status", sa.Enum("ONGOING", "COMPLETED", "DROPPED", name="enrollmentstatus")), sa.Column("score", sa.Float()))
    op.create_index("ix_training_enrollments_trainee_id", "training_enrollments", ["trainee_id"]); op.create_index("ix_training_enrollments_program_id", "training_enrollments", ["program_id"]); op.create_index("ix_training_enrollments_status", "training_enrollments", ["status"])
    op.create_table("employment_records", sa.Column("employment_id", sa.Integer(), primary_key=True), sa.Column("trainee_id", sa.Integer(), sa.ForeignKey("trainees.trainee_id"), nullable=False), sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employers.employer_id"), nullable=False), sa.Column("job_role", sa.String(200), nullable=False), sa.Column("salary", sa.Float(), nullable=False), sa.Column("joining_date", sa.DateTime()), sa.Column("status", sa.Enum("EMPLOYED", "RESIGNED", "TERMINATED", name="employmentstatus")))
    op.create_index("ix_employment_records_trainee_id", "employment_records", ["trainee_id"]); op.create_index("ix_employment_records_employer_id", "employment_records", ["employer_id"]); op.create_index("ix_employment_records_status", "employment_records", ["status"])
    op.create_table("followups", sa.Column("followup_id", sa.Integer(), primary_key=True), sa.Column("trainee_id", sa.Integer(), sa.ForeignKey("trainees.trainee_id"), nullable=False), sa.Column("follow_up_type", sa.Enum("DAY_30", "DAY_90", "DAY_180", name="followuptype"), nullable=False), sa.Column("status", sa.Enum("EMPLOYED", "UNEMPLOYED", "SELF_EMPLOYED", "FURTHER_TRAINING", name="followupstatus"), nullable=False), sa.Column("salary", sa.Float()), sa.Column("feedback", sa.Text()), sa.Column("created_at", sa.DateTime()))
    op.create_index("ix_followups_trainee_id", "followups", ["trainee_id"]); op.create_index("ix_followups_follow_up_type", "followups", ["follow_up_type"])

def downgrade():
    for table in ("followups", "employment_records", "training_enrollments", "trainee_skills", "training_programs", "trainees", "employers", "skills", "users"):
        op.drop_table(table)
