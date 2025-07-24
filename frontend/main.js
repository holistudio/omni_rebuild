import { createApp, h } from 'vue';

const App = {
  name: 'App',
  render() {
    return h('div', [
      h('h1', 'OmniRebuild Chatbot'),
      h('div', {
        style: {
          background: '#fbe9c6',
          borderRadius: '12px',
          padding: '2rem',
          marginTop: '1rem',
          minHeight: '200px',
          width: '100%',
          boxShadow: '0 2px 12px rgba(124, 74, 3, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#6d4c1b',
          fontSize: '1.1rem',
        }
      }, 'Chatbot UI will appear here (Phase 0)')
    ]);
  }
};

createApp(App).mount('#app'); 