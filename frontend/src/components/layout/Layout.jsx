import React from 'react';
import Header from './Header';
import Breadcrumb from './Breadcrumb';

const Layout = ({ children, breadcrumbItems }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Breadcrumb items={breadcrumbItems} />
        {children}
      </main>
    </div>
  );
};

export default Layout;