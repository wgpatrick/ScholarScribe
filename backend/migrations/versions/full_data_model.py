"""implement full data model

Revision ID: full_data_model
Revises: 783d84e916bf
Create Date: 2025-03-12 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
import enum

# revision identifiers, used by Alembic.
revision = 'full_data_model_' + str(uuid.uuid4())[:8]
down_revision = '783d84e916bf'
branch_labels = None
depends_on = None


def upgrade():
    # First - modify existing documents table
    
    # Remove old uuid column
    op.drop_index('ix_documents_uuid', table_name='documents')
    op.drop_column('documents', 'uuid')
    
    # Change id to UUID and add new columns
    op.alter_column('documents', 'id',
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using="id::uuid",
        existing_server_default=None)
    
    # Rename markdown_text to markdown_content
    op.alter_column('documents', 'markdown_text',
        new_column_name='markdown_content',
        existing_type=sa.Text(),
        existing_nullable=True)
    
    # Rename conversion_status to processing_status
    op.alter_column('documents', 'conversion_status',
        new_column_name='processing_status',
        existing_type=sa.String(),
        existing_nullable=True)
    
    # Add new columns to documents table
    op.add_column('documents', sa.Column('abstract', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('publication_date', sa.Date(), nullable=True))
    op.add_column('documents', sa.Column('journal_or_conference', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('doi', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('pdf_hash', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('pdf_size', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('raw_text', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('parsing_method', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('parsing_error', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('processing_time', sa.Float(), nullable=True))
    op.add_column('documents', sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('documents', sa.Column('view_count', sa.Integer(), server_default='0', nullable=True))
    op.add_column('documents', sa.Column('created_by', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('is_public', sa.Boolean(), server_default='false', nullable=True))
    
    # Update authors field to JSONB
    op.alter_column('documents', 'authors',
        type_=postgresql.JSONB(),
        postgresql_using="to_jsonb(string_to_array(authors, ','))",
        existing_type=sa.String(),
        existing_nullable=True)
    
    # Create sections table
    op.create_table('sections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('has_equations', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('has_figures', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('has_tables', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('keywords', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['sections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sections_document_id'), 'sections', ['document_id'], unique=False)
    op.create_index(op.f('ix_sections_title'), 'sections', ['title'], unique=False)
    
    # Create notes table
    op.create_table('notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('start_offset', sa.Integer(), nullable=False),
        sa.Column('end_offset', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_document_id'), 'notes', ['document_id'], unique=False)
    op.create_index(op.f('ix_notes_section_id'), 'notes', ['section_id'], unique=False)
    
    # Create comments table
    op.create_table('comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('anchor_text', sa.Text(), nullable=False),
        sa.Column('start_offset', sa.Integer(), nullable=False),
        sa.Column('end_offset', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_document_id'), 'comments', ['document_id'], unique=False)
    op.create_index(op.f('ix_comments_section_id'), 'comments', ['section_id'], unique=False)
    
    # Create annotations table
    op.create_table('annotations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('annotation_text', sa.Text(), nullable=False),
        sa.Column('annotation_type', sa.Enum('definition', 'explanation', 'context', 'summary', 'other', name='annotationtype'), nullable=True),
        sa.Column('start_offset', sa.Integer(), nullable=False),
        sa.Column('end_offset', sa.Integer(), nullable=False),
        sa.Column('model_used', sa.String(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annotations_document_id'), 'annotations', ['document_id'], unique=False)
    op.create_index(op.f('ix_annotations_section_id'), 'annotations', ['section_id'], unique=False)
    
    # Create references table
    op.create_table('references',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('raw_citation', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('authors', postgresql.JSONB(), nullable=True),
        sa.Column('publication_year', sa.Integer(), nullable=True),
        sa.Column('journal_or_conference', sa.String(), nullable=True),
        sa.Column('volume', sa.String(), nullable=True),
        sa.Column('issue', sa.String(), nullable=True),
        sa.Column('pages', sa.String(), nullable=True),
        sa.Column('doi', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('citation_count', sa.Integer(), nullable=True),
        sa.Column('appears_in_sections', postgresql.JSONB(), nullable=True),
        sa.Column('citation_contexts', postgresql.JSONB(), nullable=True),
        sa.Column('metadata_status', sa.Enum('not_fetched', 'pending', 'fetched', 'failed', name='metadatastatus'), nullable=True),
        sa.Column('last_metadata_update', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_references_document_id'), 'references', ['document_id'], unique=False)
    op.create_index(op.f('ix_references_doi'), 'references', ['doi'], unique=False)
    
    # Create figures table
    op.create_table('figures',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('figure_type', sa.Enum('figure', 'table', 'equation', 'chart', 'diagram', 'other', name='figuretype'), nullable=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('image_path', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('reference_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_figures_document_id'), 'figures', ['document_id'], unique=False)
    op.create_index(op.f('ix_figures_section_id'), 'figures', ['section_id'], unique=False)
    
    # Create share_links table
    op.create_table('share_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('unique_key', sa.String(), nullable=False),
        sa.Column('access_level', sa.Enum('read_only', 'comment', 'edit', name='accesslevel'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_key')
    )
    op.create_index(op.f('ix_share_links_document_id'), 'share_links', ['document_id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_table('share_links')
    op.drop_table('figures')
    op.drop_table('references')
    op.drop_table('annotations')
    op.drop_table('comments')
    op.drop_table('notes')
    op.drop_table('sections')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS accesslevel')
    op.execute('DROP TYPE IF EXISTS figuretype')
    op.execute('DROP TYPE IF EXISTS metadatastatus')
    op.execute('DROP TYPE IF EXISTS annotationtype')
    
    # Revert changes to documents table
    
    # Revert authors field to String
    op.alter_column('documents', 'authors',
        type_=sa.String(),
        postgresql_using="array_to_string(authors, ',')",
        existing_type=postgresql.JSONB(),
        existing_nullable=True)
    
    # Remove new columns from documents table
    op.drop_column('documents', 'is_public')
    op.drop_column('documents', 'created_by')
    op.drop_column('documents', 'view_count')
    op.drop_column('documents', 'last_viewed_at')
    op.drop_column('documents', 'processing_time')
    op.drop_column('documents', 'parsing_error')
    op.drop_column('documents', 'parsing_method')
    op.drop_column('documents', 'raw_text')
    op.drop_column('documents', 'pdf_size')
    op.drop_column('documents', 'pdf_hash')
    op.drop_column('documents', 'doi')
    op.drop_column('documents', 'journal_or_conference')
    op.drop_column('documents', 'publication_date')
    op.drop_column('documents', 'abstract')
    
    # Revert renamed columns
    op.alter_column('documents', 'processing_status',
        new_column_name='conversion_status',
        existing_type=sa.String(),
        existing_nullable=True)
        
    op.alter_column('documents', 'markdown_content',
        new_column_name='markdown_text',
        existing_type=sa.Text(),
        existing_nullable=True)
    
    # Revert id to Integer
    op.alter_column('documents', 'id',
        type_=sa.Integer(),
        postgresql_using="id::integer",
        existing_server_default=None)
    
    # Add back the uuid column
    op.add_column('documents', sa.Column('uuid', sa.String(), nullable=True))
    op.create_index('ix_documents_uuid', 'documents', ['uuid'], unique=True)