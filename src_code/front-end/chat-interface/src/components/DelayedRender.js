import React, { useState, useEffect } from 'react';

const DelayedRender = ({ children, speed = 100 }) => {
  const [visibleChildren, setVisibleChildren] = useState([]);

  useEffect(() => {
    const elements = React.Children.toArray(children); // Convert children to an array
    let index = 0;

    // Reset the visibleChildren before starting the render cycle
    setVisibleChildren([]);

    // Define a function to render children one by one with a delay
    const renderNextChild = () => {
      if (index < elements.length) {
        setVisibleChildren((prev) => [...prev, elements[index]]);
        index++;

        // Schedule the next child to be rendered after `speed` delay
        setTimeout(renderNextChild, speed);
      }
    };

    // Start rendering the first child
    renderNextChild();

    // Cleanup function to reset the state and clear timeouts if component is unmounted or children change
    return () => {
      setVisibleChildren([]); // Clear the visible children
    };
  }, [children, speed]); // Re-run effect when children or speed change

  return <div>{visibleChildren}</div>;
};

export default DelayedRender;
