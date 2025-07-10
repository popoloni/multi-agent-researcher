import React from 'react';
import Layout from '../components/layout/Layout';
import ObioneChat from '../components/chat/ObioneChat';

const Chat = () => {
  return (
    <Layout>
      <div className="h-full">
        <ObioneChat />
      </div>
    </Layout>
  );
};

export default Chat;