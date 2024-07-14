import React, { useState } from 'react';

const MenuItem = ({ item }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (item.children) {
    return (
      <div>
        <button onClick={() => setIsOpen(!isOpen)}>
          {item.name} {isOpen ? '▼' : '▶'}
        </button>
        {isOpen && (
          <div className="ml-4">
            {item.children.map((child, index) => (
              <MenuItem key={index} item={child} />
            ))}
          </div>
        )}
      </div>
    );
  } else {
    return <div>{item.name}</div>;
  }
};

const Sidebar = () => {
  const menuItems = [
    {
      name: 'Dashboard',
      children: [
        { name: 'Analytics' },
        { name: 'Reports' },
      ],
    },
    {
      name: 'Projects',
      children: [
        { name: 'Active' },
        { name: 'Archived' },
      ],
    },
    { name: 'Settings' },
  ];

  return (
    <div className="sidebar">
      <h2>Menu</h2>
      {menuItems.map((item, index) => (
        <MenuItem key={index} item={item} />
      ))}
    </div>
  );
};

export default Sidebar;
