import { useState, useEffect } from 'react';

const ReadingProgress = () => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      // Calculate how far the user has scrolled
      const scrollTop = window.scrollY;
      const docHeight = 
        document.documentElement.scrollHeight - 
        document.documentElement.clientHeight;
      
      // Calculate the percentage (clamped between 0 and 100)
      const scrollPercent = scrollTop / docHeight * 100;
      setProgress(Math.min(100, Math.max(0, scrollPercent)));
    };

    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);
    
    // Initial calculation
    handleScroll();
    
    // Clean up
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <div className="h-1 bg-gray-100 w-full sticky top-0 z-20">
      <div 
        className="h-1 bg-primary-500 transition-all duration-150 ease-out"
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );
};

export default ReadingProgress;