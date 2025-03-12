"""New schema with UUID primary keys

Revision ID: new_data_model
Revises: 783d84e916bf
Create Date: 2025-03-12 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
import enum

# revision identifiers
revision = 'new_data_model_' + uuid.uuid4().hex[:8]
down_revision = '783d84e916bf'
branch_labels = None
depends_on = None


def upgrade():
    # =============== STEP 1: DROP existing table ===============
    # Drop the existing documents table (it only has test data anyway)
    op.drop_table('documents')

    # =============== STEP 2: Create document table with UUID primary key ===============
    op.create_table('documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('authors', postgresql.JSONB(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('journal_or_conference', sa.String(), nullable=True),
        sa.Column('doi', sa.String(), nullable=True),
        
        # Storage
        sa.Column('pdf_path', sa.String(), nullable=False),
        sa.Column('pdf_hash', sa.String(), nullable=True),
        sa.Column('pdf_size', sa.Integer(), nullable=True),
        
        # Content
        sa.Column('markdown_content', sa.Text(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        
        # Processing metadata
        sa.Column('processing_status', sa.String(), nullable=True),
        sa.Column('parsing_method', sa.String(), nullable=True),
        sa.Column('parsing_error', sa.Text(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        
        # Timestamps and metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=True),
        
        # Owner/creator information
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='false', nullable=True),
    )
    
    # Add indexes
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)
    
    # =============== STEP 3: Create sections table ===============
    op.create_table('sections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
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
    )
    op.create_index(op.f('ix_sections_document_id'), 'sections', ['document_id'], unique=False)
    op.create_index(op.f('ix_sections_title'), 'sections', ['title'], unique=False)
    
    # =============== STEP 4: Create notes table ===============
    op.create_table('notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
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
    )
    op.create_index(op.f('ix_notes_document_id'), 'notes', ['document_id'], unique=False)
    op.create_index(op.f('ix_notes_section_id'), 'notes', ['section_id'], unique=False)
    
    # =============== STEP 5: Create comments table ===============
    op.create_table('comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
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
    )
    op.create_index(op.f('ix_comments_document_id'), 'comments', ['document_id'], unique=False)
    op.create_index(op.f('ix_comments_section_id'), 'comments', ['section_id'], unique=False)
    
    # =============== STEP 6: Create annotations table ===============
    # Create enum for annotation type
    annotation_type = postgresql.ENUM('definition', 'explanation', 'context', 'summary', 'other', name='annotationtype')
    annotation_type.create(op.get_bind())
    
    op.create_table('annotations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
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
    )
    op.create_index(op.f('ix_annotations_document_id'), 'annotations', ['document_id'], unique=False)
    op.create_index(op.f('ix_annotations_section_id'), 'annotations', ['section_id'], unique=False)
    
    # =============== STEP 7: Create references table ===============
    # Create enum for metadata status
    metadata_status = postgresql.ENUM('not_fetched', 'pending', 'fetched', 'failed', name='metadatastatus')
    metadata_status.create(op.get_bind())
    
    op.create_table('references',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
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
    )
    op.create_index(op.f('ix_references_document_id'), 'references', ['document_id'], unique=False)
    op.create_index(op.f('ix_references_doi'), 'references', ['doi'], unique=False)
    
    # =============== STEP 8: Create figures table ===============
    # Create enum for figure type
    figure_type = postgresql.ENUM('figure', 'table', 'equation', 'chart', 'diagram', 'other', name='figuretype')
    figure_type.create(op.get_bind())
    
    op.create_table('figures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
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
    )
    op.create_index(op.f('ix_figures_document_id'), 'figures', ['document_id'], unique=False)
    op.create_index(op.f('ix_figures_section_id'), 'figures', ['section_id'], unique=False)
    
    # =============== STEP 9: Create share_links table ===============
    # Create enum for access level
    access_level = postgresql.ENUM('read_only', 'comment', 'edit', name='accesslevel')
    access_level.create(op.get_bind())
    
    op.create_table('share_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
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
    op.drop_table('documents')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS accesslevel')
    op.execute('DROP TYPE IF EXISTS figuretype')
    op.execute('DROP TYPE IF EXISTS metadatastatus')
    op.execute('DROP TYPE IF EXISTS annotationtype')