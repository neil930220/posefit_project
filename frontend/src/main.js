import { createApp } from 'vue'
import App    from './App.vue'
import router from './router'
import CombinedAuth from './components/CombinedAuth.vue';
import HistoryList from './components/HistoryList.vue'

const app = createApp(App);
app.use(router)
app.component('CombinedAuth', CombinedAuth);
app.mount('#app');

const container = document.getElementById('history-list')
if (container) {
  const apiUrl = container.dataset.apiUrl
  createApp(HistoryList, { apiUrl }).mount(container)
}