import { createApp } from 'vue'
import App    from './App.vue'
import router from './router'
import CombinedAuth from './components/CombinedAuth.vue';
import HistoryList from './components/HistoryList.vue'

const app = createApp(App);
app.use(router)
app.component('CombinedAuth', CombinedAuth);
app.component('HistoryList',  HistoryList)
app.mount('#app');
