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
    const bookRows = chunk(this.books.filter(b => b.thumbnail), 4);

    return h('div', { class: 'bookshelf-container' }, [
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
};

createApp(App).mount('#app');
