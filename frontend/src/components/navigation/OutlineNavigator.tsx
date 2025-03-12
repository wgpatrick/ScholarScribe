import { useState } from 'react';
import { useDocument } from '../../context/DocumentContext';
import { useUI } from '../../context/UIContext';

interface OutlineNavigatorProps {
  className?: string;
}

const OutlineNavigator = ({ className = '' }: OutlineNavigatorProps) => {
  const { sections, currentSection, setCurrentSection } = useDocument();
  const { isOutlineSidebarOpen } = useUI();
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});

  if (!isOutlineSidebarOpen) {
    return null;
  }

  // Group sections by parent to build a tree
  const sectionsByParent: Record<string | null, typeof sections> = {};
  sections.forEach(section => {
    const parentId = section.parent_id || null;
    if (!sectionsByParent[parentId]) {
      sectionsByParent[parentId] = [];
    }
    sectionsByParent[parentId].push(section);
  });

  // Sort sections by order within each parent group
  Object.keys(sectionsByParent).forEach(parentId => {
    sectionsByParent[parentId].sort((a, b) => a.order - b.order);
  });

  // Handle section click
  const handleSectionClick = (sectionId: string) => {
    setCurrentSection(sectionId);
    
    // Find the section element and scroll to it
    const sectionElement = document.getElementById(`section-${sectionId}`);
    if (sectionElement) {
      sectionElement.scrollIntoView({ behavior: 'smooth' });
    }

    // Toggle expanded state for sections with children
    if (sectionsByParent[sectionId] && sectionsByParent[sectionId].length > 0) {
      setExpandedSections(prev => ({
        ...prev,
        [sectionId]: !prev[sectionId]
      }));
    }
  };

  // Recursive function to render the section tree
  const renderSections = (parentId: string | null = null, level = 0): JSX.Element => {
    const parentSections = sectionsByParent[parentId] || [];
    
    if (parentSections.length === 0) {
      return <></>;
    }
    
    return (
      <ul className={`space-y-1 ${level > 0 ? 'ml-4' : ''}`}>
        {parentSections.map(section => {
          const hasChildren = sectionsByParent[section.id] && sectionsByParent[section.id].length > 0;
          const isExpanded = expandedSections[section.id] || false;
          const isActive = currentSection === section.id;
          
          return (
            <li key={section.id}>
              <div 
                className={`flex items-center py-1 px-2 rounded-md cursor-pointer text-sm ${
                  isActive 
                    ? 'bg-primary-50 text-primary-700 font-medium' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                onClick={() => handleSectionClick(section.id)}
              >
                {hasChildren && (
                  <span className="mr-1 text-gray-400">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                )}
                <span className="truncate">
                  {section.title}
                </span>
                {section.has_figures && (
                  <span className="ml-1 text-xs text-gray-500" title="Contains figures">📊</span>
                )}
                {section.has_tables && (
                  <span className="ml-1 text-xs text-gray-500" title="Contains tables">📋</span>
                )}
                {section.has_equations && (
                  <span className="ml-1 text-xs text-gray-500" title="Contains equations">📐</span>
                )}
              </div>
              
              {hasChildren && isExpanded && renderSections(section.id, level + 1)}
            </li>
          );
        })}
      </ul>
    );
  };

  return (
    <div className={`w-64 border-r border-gray-200 bg-gray-50 overflow-y-auto p-4 ${className}`}>
      <h2 className="text-lg font-bold mb-4">Outline</h2>
      
      {sections.length === 0 ? (
        <p className="text-gray-500 text-sm">No sections available</p>
      ) : (
        renderSections()
      )}
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <button
          className="btn btn-secondary text-sm w-full"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          Back to Top
        </button>
      </div>
    </div>
  );
};

export default OutlineNavigator;