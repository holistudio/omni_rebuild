import { createApp, h, ref, onMounted } from 'vue';

const BACKEND_URL = 'http://localhost:5000';

const App = {
  name: 'App',
  setup() {
    const userInput = ref('');
    const questions = ref([]);
    const currentQuestionIndex = ref(0);
    const loading = ref(true);
    const error = ref(null);
    const answers = ref([]);

    // Fetch questions from backend only
    const fetchQuestions = async () => {
      loading.value = true;
      try {
        const res = await fetch(`${BACKEND_URL}/questions`);
        const data = await res.json();
        questions.value = data.questions || [];
        currentQuestionIndex.value = 0;
        loading.value = false;
        if (!questions.value.length) {
          error.value = 'No questions available from the database.';
        }
      } catch (e) {
        error.value = 'Failed to load questions from the backend.';
        loading.value = false;
      }
    };

    onMounted(fetchQuestions);

    // Handle user input submit
    const handleInput = (e) => {
      e.preventDefault();
      if (!userInput.value.trim()) return;
      const logEntry = {
        q_index: currentQuestionIndex.value,
        question: questions.value[currentQuestionIndex.value],
        response: userInput.value
      };
      answers.value.push(logEntry);
      // Save to localStorage
      try {
        localStorage.setItem('omni_conversation', JSON.stringify(answers.value));
      } catch (err) {
        // Ignore localStorage errors
      }
      userInput.value = '';
      if (currentQuestionIndex.value < questions.value.length - 1) {
        currentQuestionIndex.value++;
      }
    };

    return { userInput, questions, currentQuestionIndex, loading, error, handleInput };
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
          minHeight: '300px',
          width: '100%',
          maxWidth: '420px',
          boxShadow: '0 4px 32px rgba(80, 60, 20, 0.12)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
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
            minHeight: '60px',
            textAlign: 'center',
          }
        },
          this.loading ? 'Loading questions...' :
          this.error ? this.error :
          (this.questions[this.currentQuestionIndex] || 'No questions available.')
        ),
        h('form', {
          style: {
            width: '100%',
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            marginTop: '2rem',
          },
          onSubmit: this.handleInput
        }, [
          h('textarea', {
            placeholder: 'Type your answer...',
            style: {
              flex: 1,
              maxWidth: '260px',
              minHeight: '60px',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              border: '1px solid #e0cfa6',
              background: '#fffbe9',
              color: '#6d4c1b',
              fontSize: '1rem',
              boxShadow: '0 1px 4px rgba(124, 74, 3, 0.04)',
              outline: 'none',
              textAlign: 'center',
              resize: 'vertical',
            },
            value: this.userInput,
            onInput: e => { this.userInput = e.target.value; },
            disabled: this.loading || this.error,
            onKeydown: e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                // Submit the form
                const form = e.target.form;
                if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
              }
            }
          }),
          h('button', {
            type: 'submit',
            style: {
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              border: 'none',
              background: '#e0cfa6',
              color: '#7c4a03',
              fontWeight: 'bold',
              fontSize: '1.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 1px 4px rgba(124, 74, 3, 0.08)',
              transition: 'background 0.2s',
            },
            disabled: this.loading || this.error
          }, '↑')
        ])
      ])
    ]);
  }
};

createApp(App).mount('#app'); 