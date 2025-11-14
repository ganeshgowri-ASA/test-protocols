"""Initial schema for test protocols

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema"""

    # Create protocols table
    op.create_table(
        'protocols',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('standard', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('json_template', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_protocols_id'), 'protocols', ['id'], unique=False)
    op.create_index(op.f('ix_protocols_protocol_id'), 'protocols', ['protocol_id'], unique=True)

    # Create equipment table
    op.create_table(
        'equipment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('equipment_type', sa.String(length=100), nullable=False),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_equipment_id'), 'equipment', ['equipment_id'], unique=True)
    op.create_index(op.f('ix_equipment_id'), 'equipment', ['id'], unique=False)

    # Create equipment_calibrations table
    op.create_table(
        'equipment_calibrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.Integer(), nullable=False),
        sa.Column('calibration_date', sa.DateTime(), nullable=False),
        sa.Column('calibration_due_date', sa.DateTime(), nullable=False),
        sa.Column('calibration_certificate', sa.String(length=200), nullable=True),
        sa.Column('performed_by', sa.String(length=100), nullable=True),
        sa.Column('calibration_standard', sa.String(length=200), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_calibrations_calibration_date'), 'equipment_calibrations', ['calibration_date'], unique=False)
    op.create_index(op.f('ix_equipment_calibrations_calibration_due_date'), 'equipment_calibrations', ['calibration_due_date'], unique=False)
    op.create_index(op.f('ix_equipment_calibrations_id'), 'equipment_calibrations', ['id'], unique=False)

    # Create test_runs table
    op.create_table(
        'test_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.String(length=100), nullable=False),
        sa.Column('protocol_id', sa.Integer(), nullable=False),
        sa.Column('module_serial_number', sa.String(length=100), nullable=False),
        sa.Column('module_manufacturer', sa.String(length=100), nullable=True),
        sa.Column('module_model', sa.String(length=100), nullable=True),
        sa.Column('module_nameplate_power', sa.Float(), nullable=True),
        sa.Column('module_manufacturing_date', sa.DateTime(), nullable=True),
        sa.Column('operator_name', sa.String(length=100), nullable=False),
        sa.Column('operator_certification', sa.String(length=100), nullable=True),
        sa.Column('test_facility', sa.String(length=200), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'ABORTED', name='teststatus'), nullable=True),
        sa.Column('pass_fail', sa.Boolean(), nullable=True),
        sa.Column('power_degradation_percent', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('initial_voc', sa.Float(), nullable=True),
        sa.Column('initial_isc', sa.Float(), nullable=True),
        sa.Column('initial_pmax', sa.Float(), nullable=True),
        sa.Column('initial_fill_factor', sa.Float(), nullable=True),
        sa.Column('final_voc', sa.Float(), nullable=True),
        sa.Column('final_isc', sa.Float(), nullable=True),
        sa.Column('final_pmax', sa.Float(), nullable=True),
        sa.Column('final_fill_factor', sa.Float(), nullable=True),
        sa.Column('initial_insulation_resistance', sa.Float(), nullable=True),
        sa.Column('final_insulation_resistance', sa.Float(), nullable=True),
        sa.Column('wet_leakage_current', sa.Float(), nullable=True),
        sa.Column('qr_code', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['protocol_id'], ['protocols.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_runs_id'), 'test_runs', ['id'], unique=False)
    op.create_index(op.f('ix_test_runs_module_serial_number'), 'test_runs', ['module_serial_number'], unique=False)
    op.create_index(op.f('ix_test_runs_test_id'), 'test_runs', ['test_id'], unique=True)

    # Create measurements table
    op.create_table(
        'measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_run_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('parameter', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_measurements_id'), 'measurements', ['id'], unique=False)
    op.create_index(op.f('ix_measurements_parameter'), 'measurements', ['parameter'], unique=False)
    op.create_index(op.f('ix_measurements_timestamp'), 'measurements', ['timestamp'], unique=False)

    # Create visual_inspections table
    op.create_table(
        'visual_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_run_id', sa.Integer(), nullable=False),
        sa.Column('inspection_type', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('inspector', sa.String(length=100), nullable=False),
        sa.Column('defects', sa.JSON(), nullable=True),
        sa.Column('photographs', sa.JSON(), nullable=True),
        sa.Column('severity', sa.Enum('NONE', 'MINOR', 'MAJOR', name='defectseverity'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visual_inspections_id'), 'visual_inspections', ['id'], unique=False)

    # Create hot_spot_tests table
    op.create_table(
        'hot_spot_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_run_id', sa.Integer(), nullable=False),
        sa.Column('cell_id', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('target_temperature', sa.Float(), nullable=True),
        sa.Column('max_temperature_reached', sa.Float(), nullable=True),
        sa.Column('reverse_bias_voltage', sa.Float(), nullable=True),
        sa.Column('current_limit', sa.Float(), nullable=True),
        sa.Column('temperature_profile', sa.JSON(), nullable=True),
        sa.Column('thermal_images', sa.JSON(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hot_spot_tests_id'), 'hot_spot_tests', ['id'], unique=False)


def downgrade() -> None:
    """Drop all tables"""
    op.drop_index(op.f('ix_hot_spot_tests_id'), table_name='hot_spot_tests')
    op.drop_table('hot_spot_tests')
    op.drop_index(op.f('ix_visual_inspections_id'), table_name='visual_inspections')
    op.drop_table('visual_inspections')
    op.drop_index(op.f('ix_measurements_timestamp'), table_name='measurements')
    op.drop_index(op.f('ix_measurements_parameter'), table_name='measurements')
    op.drop_index(op.f('ix_measurements_id'), table_name='measurements')
    op.drop_table('measurements')
    op.drop_index(op.f('ix_test_runs_test_id'), table_name='test_runs')
    op.drop_index(op.f('ix_test_runs_module_serial_number'), table_name='test_runs')
    op.drop_index(op.f('ix_test_runs_id'), table_name='test_runs')
    op.drop_table('test_runs')
    op.drop_index(op.f('ix_equipment_calibrations_calibration_due_date'), table_name='equipment_calibrations')
    op.drop_index(op.f('ix_equipment_calibrations_calibration_date'), table_name='equipment_calibrations')
    op.drop_index(op.f('ix_equipment_calibrations_id'), table_name='equipment_calibrations')
    op.drop_table('equipment_calibrations')
    op.drop_index(op.f('ix_equipment_id'), table_name='equipment')
    op.drop_index(op.f('ix_equipment_equipment_id'), table_name='equipment')
    op.drop_table('equipment')
    op.drop_index(op.f('ix_protocols_protocol_id'), table_name='protocols')
    op.drop_index(op.f('ix_protocols_id'), table_name='protocols')
    op.drop_table('protocols')
