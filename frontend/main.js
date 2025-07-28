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
    const books = ref([]);
    const view = ref('chat'); // 'chat' or 'results'
    const selectedBook = ref(null);

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

    const handleInput = async (e) => {
      e.preventDefault();
      if (!userInput.value.trim()) return;
      const logEntry = {
        q_index: currentQuestionIndex.value,
        question: questions.value[currentQuestionIndex.value],
        response: userInput.value
      };
      answers.value.push(logEntry);
      localStorage.setItem('omni_conversation', JSON.stringify(answers.value));
      userInput.value = '';

      if (currentQuestionIndex.value < questions.value.length - 1) {
        currentQuestionIndex.value++;
      } else {
        loading.value = true;
        try {
          await fetch(`${BACKEND_URL}/save_conversation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conversation: answers.value })
          });

          const res = await fetch(`${BACKEND_URL}/search_books`);
          const data = await res.json();
          books.value = data.books || [];
          view.value = 'results';
          document.getElementById('app').classList.add('results-view');
        } catch (err) {
          error.value = 'Failed to get book recommendations.';
        }
        loading.value = false;
      }
    };

    const openPanel = (book) => {
      selectedBook.value = book;
    };

    const closePanel = () => {
      selectedBook.value = null;
    };

    return { userInput, questions, currentQuestionIndex, loading, error, handleInput, books, view, selectedBook, openPanel, closePanel };
  },
  render() {
    if (this.view === 'results') {
      const chunk = (arr, size) =>
        Array.from({ length: Math.ceil(arr.length / size) }, (v, i) =>
          arr.slice(i * size, i * size + size)
        );
      const bookRows = chunk(this.books.filter(b => b.thumbnail), 4);

      return h('div', { 
        class: 'bookshelf-container' ,
        style: {
          minHeight: '80%',
          width: '100%'
        }
      }, [
        h('h1', 'Here are some books you might like:'),
        ...bookRows.flatMap(row => [
          h('div', { class: 'book-row' },
            row.map(book => h('img', {
              class: 'book-thumbnail',
              src: book.thumbnail,
              alt: book.title,
              title: book.title,
              onClick: () => this.openPanel(book),
            }))
          ),
          h('div', { class: 'shelf' })
        ]),
        this.selectedBook && h('div', { class: `details-panel ${this.selectedBook ? 'open' : ''}` }, [
          h('button', { class: 'close-btn', onClick: this.closePanel }, '×'),
          h('h2', this.selectedBook.title),
          h('h3', this.selectedBook.authors ? this.selectedBook.authors.join(', ') : 'Unknown Author'),
          h('p', this.selectedBook.description || 'No description available.')
        ])
      ]);
    }

    return h('div', { 
      id: 'chatbox' , 
      style: {
          minHeight: '80%',
          width: '100%'
        }
      }, [
      h('img', { src: 'img/logo.png', alt: 'Omni Logo', style: { width: '120px', margin: '0 auto 20px', display: 'block' } }),
      h('div', {
        id: 'convo',
        style: {
          background: '#fbe9c6',
          borderRadius: '12px',
          padding: '2rem',
          marginTop: '1rem',
          height: '100%',
          boxShadow: '0 4px 32px rgba(80, 60, 20, 0.12)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#6d4c1b',
          fontSize: '2rem',
          position: 'relative',
        }
      }, [
        h('div', {
          id: 'chatbot-output',
          style: {
            height: '80%',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
          }
        },
          this.loading ? 'Hmm, let me see...!' :
          this.error ? this.error :
          (this.questions[this.currentQuestionIndex] || 'No questions available.')
        ),
        h('form', {
          style: {
            height: '20%',
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
              maxWidth: '80%',
              minHeight: '100%',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              border: '1px solid #e0cfa6',
              background: '#fffbe9',
              color: '#6d4c1b',
              fontSize: '2rem',
              boxShadow: '0 1px 4px rgba(124, 74, 3, 0.04)',
              outline: 'none',
              textAlign: 'left',
              resize: 'vertical',
            },
            value: this.userInput,
            onInput: e => { this.userInput = e.target.value; },
            disabled: this.loading || this.error,
            onKeydown: e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
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
              fontSize: '2rem',
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