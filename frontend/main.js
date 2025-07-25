import { createApp, h, ref } from 'vue';

const App = {
  name: 'App',
  setup() {
    const userInput = ref('');
    return { userInput };
  },
  render() {
    return h('div', [
      h('h1', 'Omni'),
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
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'space-between',
          color: '#6d4c1b',
          fontSize: '1.1rem',
          position: 'relative',
        }
      }, [
        h('div', {
          style: {
            flex: 1,
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '2.5rem',
          }
        }, 'Hello there!'),
        h('input', {
          type: 'text',
          placeholder: 'Type your message...',
          style: {
            position: 'absolute',
            bottom: '1.5rem',
            left: '2rem',
            right: '2rem',
            width: 'calc(100% - 4rem)',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: '1px solid #e0cfa6',
            background: '#fffbe9',
            color: '#6d4c1b',
            fontSize: '1rem',
            boxShadow: '0 1px 4px rgba(124, 74, 3, 0.04)',
            outline: 'none',
          },
          value: this.userInput,
          onInput: e => { this.userInput = e.target.value; }
        })
      ])
    ]);
  }
};

createApp(App).mount('#app'); 