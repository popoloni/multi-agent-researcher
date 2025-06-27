import React from 'react';
import Layout from '../components/layout/Layout';
import KenobiChat from '../components/chat/KenobiChat';

const Chat = () => {
  return (
    <Layout>
      <div className="h-full">
        <KenobiChat />
      </div>
    </Layout>
  );
};

export default Chat;