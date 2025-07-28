import { createApp, h, ref, onMounted } from 'vue';

const App = {
  name: 'App',
  setup() {
    const books = ref([]);
    const selectedBook = ref(null);

    onMounted(() => {
      const storedBooks = localStorage.getItem('omni_books');
      if (storedBooks) {
        books.value = JSON.parse(storedBooks);
      }
    });

    const openPanel = (book) => {
      selectedBook.value = book;
    };

    const closePanel = () => {
      selectedBook.value = null;
    };

    return { books, selectedBook, openPanel, closePanel };
  },
  render() {
    const chunk = (arr, size) =>
      Array.from({ length: Math.ceil(arr.length / size) }, (v, i) =>
        arr.slice(i * size, i * size + size)
      );
    const bookRows = chunk(this.books, 4);

    return h('div', { class: 'bookshelf-container' }, [
      h('h1', 'Here are some books you might like:'),
      ...bookRows.flatMap(row => [
        h('div', { class: 'book-row' },
          row.map(book => {
            if (book.thumbnail) {
              return h('img', {
                class: 'book-thumbnail',
                src: book.thumbnail,
                alt: book.title,
                title: book.title,
                onClick: () => this.openPanel(book),
              });
            } else {
              return h('div', {
                class: 'book-thumbnail', // Re-use class for consistent sizing and hover effect
                style: {
                  backgroundColor: '#d3c0a3',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center',
                  padding: '10px',
                  boxSizing: 'border-box',
                  color: '#4b2e05',
                  fontWeight: 'bold',
                  fontSize: '1.2rem',
                  lineHeight: '1.4',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                },
                onClick: () => this.openPanel(book),
              }, book.title || 'No Title');
            }
          })
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
};

createApp(App).mount('#app');
