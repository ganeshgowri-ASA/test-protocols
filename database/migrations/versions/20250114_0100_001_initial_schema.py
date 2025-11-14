"""Initial schema for test protocols

Revision ID: 001
Revises:
Create Date: 2025-01-14 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema"""

    # Protocols table
    op.create_table(
        'protocols',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('standard', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_protocols_protocol_id'), 'protocols', ['protocol_id'], unique=True)

    # Equipment table
    op.create_table(
        'equipment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('equipment_type', sa.String(length=100), nullable=False),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('calibration_required', sa.Boolean(), nullable=True),
        sa.Column('calibration_interval_days', sa.Integer(), nullable=True),
        sa.Column('last_calibration_date', sa.DateTime(), nullable=True),
        sa.Column('next_calibration_date', sa.DateTime(), nullable=True),
        sa.Column('calibration_certificate', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_equipment_id'), 'equipment', ['equipment_id'], unique=True)
    op.create_index(op.f('ix_equipment_next_calibration_date'), 'equipment', ['next_calibration_date'], unique=False)

    # Test runs table
    op.create_table(
        'test_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.String(length=100), nullable=False),
        sa.Column('protocol_id', sa.Integer(), nullable=False),
        sa.Column('module_serial', sa.String(length=100), nullable=False),
        sa.Column('module_manufacturer', sa.String(length=100), nullable=True),
        sa.Column('module_model', sa.String(length=100), nullable=True),
        sa.Column('operator_id', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('pass_fail', sa.Boolean(), nullable=True),
        sa.Column('power_degradation', sa.Float(), nullable=True),
        sa.Column('failure_modes', sa.JSON(), nullable=True),
        sa.Column('initial_pmax', sa.Float(), nullable=True),
        sa.Column('final_pmax', sa.Float(), nullable=True),
        sa.Column('initial_voc', sa.Float(), nullable=True),
        sa.Column('final_voc', sa.Float(), nullable=True),
        sa.Column('initial_isc', sa.Float(), nullable=True),
        sa.Column('final_isc', sa.Float(), nullable=True),
        sa.Column('initial_ff', sa.Float(), nullable=True),
        sa.Column('final_ff', sa.Float(), nullable=True),
        sa.Column('initial_insulation', sa.Float(), nullable=True),
        sa.Column('final_insulation', sa.Float(), nullable=True),
        sa.Column('qr_code', sa.String(length=200), nullable=True),
        sa.Column('report_path', sa.String(length=500), nullable=True),
        sa.Column('equipment_ids', sa.JSON(), nullable=True),
        sa.Column('calibration_status', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['protocol_id'], ['protocols.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_runs_test_id'), 'test_runs', ['test_id'], unique=True)
    op.create_index(op.f('ix_test_runs_module_serial'), 'test_runs', ['module_serial'], unique=False)
    op.create_index(op.f('ix_test_runs_start_time'), 'test_runs', ['start_time'], unique=False)

    # Measurements table
    op.create_table(
        'measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_run_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('parameter', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('phase', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_measurements_test_run_id'), 'measurements', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_measurements_timestamp'), 'measurements', ['timestamp'], unique=False)

    # Visual inspections table
    op.create_table(
        'visual_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_run_id', sa.Integer(), nullable=False),
        sa.Column('inspection_time', sa.DateTime(), nullable=False),
        sa.Column('inspection_type', sa.String(length=20), nullable=False),
        sa.Column('broken_cells', sa.Integer(), nullable=True),
        sa.Column('delamination', sa.Boolean(), nullable=True),
        sa.Column('junction_box_intact', sa.Boolean(), nullable=True),
        sa.Column('discoloration', sa.Boolean(), nullable=True),
        sa.Column('bubbles_count', sa.Integer(), nullable=True),
        sa.Column('bubbles_max_size_mm', sa.Float(), nullable=True),
        sa.Column('inspection_passed', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=True),
        sa.Column('inspector_id', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visual_inspections_test_run_id'), 'visual_inspections', ['test_run_id'], unique=False)

    # Cycle logs table
    op.create_table(
        'cycle_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_run_id', sa.Integer(), nullable=False),
        sa.Column('cycle_number', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('temp_min', sa.Float(), nullable=True),
        sa.Column('temp_max', sa.Float(), nullable=True),
        sa.Column('temp_avg', sa.Float(), nullable=True),
        sa.Column('humidity_min', sa.Float(), nullable=True),
        sa.Column('humidity_max', sa.Float(), nullable=True),
        sa.Column('humidity_avg', sa.Float(), nullable=True),
        sa.Column('temperature_excursions', sa.Integer(), nullable=True),
        sa.Column('humidity_excursions', sa.Integer(), nullable=True),
        sa.Column('excursion_details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cycle_logs_test_run_id'), 'cycle_logs', ['test_run_id'], unique=False)

    # Cycle datapoints table
    op.create_table(
        'cycle_datapoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cycle_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('chamber_status', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['cycle_id'], ['cycle_logs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cycle_datapoints_cycle_id'), 'cycle_datapoints', ['cycle_id'], unique=False)
    op.create_index(op.f('ix_cycle_datapoints_timestamp'), 'cycle_datapoints', ['timestamp'], unique=False)


def downgrade() -> None:
    """Drop all tables"""
    op.drop_index(op.f('ix_cycle_datapoints_timestamp'), table_name='cycle_datapoints')
    op.drop_index(op.f('ix_cycle_datapoints_cycle_id'), table_name='cycle_datapoints')
    op.drop_table('cycle_datapoints')

    op.drop_index(op.f('ix_cycle_logs_test_run_id'), table_name='cycle_logs')
    op.drop_table('cycle_logs')

    op.drop_index(op.f('ix_visual_inspections_test_run_id'), table_name='visual_inspections')
    op.drop_table('visual_inspections')

    op.drop_index(op.f('ix_measurements_timestamp'), table_name='measurements')
    op.drop_index(op.f('ix_measurements_test_run_id'), table_name='measurements')
    op.drop_table('measurements')

    op.drop_index(op.f('ix_test_runs_start_time'), table_name='test_runs')
    op.drop_index(op.f('ix_test_runs_module_serial'), table_name='test_runs')
    op.drop_index(op.f('ix_test_runs_test_id'), table_name='test_runs')
    op.drop_table('test_runs')

    op.drop_index(op.f('ix_equipment_next_calibration_date'), table_name='equipment')
    op.drop_index(op.f('ix_equipment_equipment_id'), table_name='equipment')
    op.drop_table('equipment')

    op.drop_index(op.f('ix_protocols_protocol_id'), table_name='protocols')
    op.drop_table('protocols')
