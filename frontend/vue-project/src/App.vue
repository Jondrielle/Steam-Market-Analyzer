<script setup>
import { ref, onMounted, onBeforeUnmount,computed} from 'vue'
import axios from 'axios'
import GameList from './components/GameList.vue'
import PriceChart from './components/PriceChart.vue'
import SearchFunction from './components/SearchFunction.vue'
import { ChartBarSquareIcon, MagnifyingGlassIcon,TrashIcon} from '@heroicons/vue/24/outline'


const priceHistory = ref([])
const searchName = ref('')
const topResults = ref([])
const gameList = ref([])
const showResults = ref(false)
const showList = ref(false)
const selectedGameId = ref(null)
const selectedPeriod = ref("daily")
const resultsBox = ref(null)
const notificationMessage = ref(null)


const selectedGameTitle = computed(()=>{
  const game = gameList.value.find(g => g.app_id === selectedGameId.value)
  return game ? game.title : ""
})

// REQUEST RESULTS
async function getResults() {
  try {
    if(searchName.value == ''){
      setTimeout(()=>{
        notificationMessage.value = `Please enter a game name to search`
      },2000)
      return
    }

    const response = await axios.get('http://localhost:8000/find', {
      params: { title: searchName.value }
    })

    console.log(response.data)  
    topResults.value = response.data
    showResults.value = true
  } catch (error) {
    console.error('Error fetching results:', error)
  }
}

// ADD GAME 
async function addResult(item) {
  try {
    const exists = gameList.value.some(
      game => game.app_id === item.app_id
    )

    if(exists){
      notificationMessage.value = `${item.title} already in your wishlist`
      setTimeout(()=>{
        notificationMessage.value = null
        },2000)
      return 
    }

    await axios.post('http://localhost:8000/add', item)
    gameList.value.push(item)
    topResults.value = []
    showResults.value = false
    searchName.value = null
    notificationMessage.value = `${item.title} was added`

    setTimeout(()=>{
      notificationMessage.value = null
      },2000)

  } catch (error) {
    console.error('Error adding game', error)
  }
}

// DELETE GAME 
async function deleteGame(item) {
  try {
    await axios.delete(`http://localhost:8000/delete/${item.app_id}`)

    console.log("Item deleted:",item)
    gameList.value = gameList.value.filter(
      game => game.app_id !== item.app_id
    )

    // 🔑 CLEAR CHART IF DELETED GAME WAS SELECTED
    if (selectedGameId.value === item.app_id) {
      selectedGameId.value = null
      priceHistory.value = []
    }

    notificationMessage.value = `${item.title} was deleted`

    setTimeout(()=>{
      notificationMessage.value = null
      },2000)
  } catch (error) {
    console.error('Delete Failed', error)
  }
}

// GAME LIST 
async function displayList() {
  try{
    const response = await axios.get('http://localhost:8000/list')
    gameList.value = response.data
  }catch(err){
    console.error("Failed to load wishlist", err)
  }
}

// REQUEST PRICE TREND 
async function showPriceHistory(gameId){
  console.log("Game Selected:", gameId)
  selectedGameId.value = gameId
  try {
    const response = await axios.get(`http://localhost:8000/games/${gameId}/price-history`, {
      params: { period: selectedPeriod.value }
    });

    console.log("FULL RESPONSE:", response.data)
    priceHistory.value = response.data.prices
    console.log("APP priceHistory:", priceHistory.value)
  } catch (err) {
    console.error("Failed to fetch price history", err);
  }
}

// TOGGLE SHOW GAME LIST 
function toggleShow() {
  showList.value = !showList.value

  if(showList.value){
    console.log("Showing List")

  }
  else{
    console.log("Hiding List")
  }
}

// SET PRICE TREND PERIOD 
function handleSetPeriod(period){
  selectedPeriod.value = period
  //console.log(`Period is ${selectedPeriod.value}`)
}

function handleCloseChart(){
  console.log("Closing the chart")
  priceHistory.value = []
}

// OUTSIDE CLICK EVENTS 
function handleClickOutside(event){
  console.log("outside click")
  if(resultsBox.value && !resultsBox.value.contains(event.target)){
    showResults.value = false
    searchName.value = null
  }
}

function getGameImage(appId){
  return `https://cdn.cloudflare.steamstatic.com/steam/apps/${appId}/capsule_sm_120.jpg`
}

async function getGameReviewInfo(appId){
  try{
    const response = await axios.get("http://store.steampowered.com/appreviews/<${appId}>?json=1")

    console.log('Response:', response)
  }catch(e){
    console.log('Error:',e)
  }
}

onMounted(()=> {
  displayList()
  document.addEventListener('click',handleClickOutside)
})

onBeforeUnmount(()=> {
  document.removeEventListener('click',handleClickOutside)
})


</script>

<template>
  <div class="max-w-6xl mx-auto p-6 space-y-6">
    <header class="bg-white rounded-xl shadow p-6">
      <div class="flex flex-col gap-3">
        <h1 class="text-2xl font-bold">Steam Price Tracker</h1>

          <div class="flex gap-2">
            <input 
              v-model="searchName" 
              placeholder="Enter game name"
              class="border rounded-xl px-3 py-2 flex-1"
            />

            <button 
              class="flex items-center gap-2 px-4 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition" 
              @click="getResults">
                <MagnifyingGlassIcon 
                  class="size-5 "/>
                  Search
            </button>
          </div>
              
          <!-- SEARCH RESULTS -->
          <div 
            ref="resultsBox" 
            v-if="showResults && topResults.length"
            class="border rounded-xl p-3 bg-white shadow"
          >
            <h3 class="font-semibold mb-2">Results</h3>
            <ul class="grid grid-cols-2 gap-2">
              <li 
                class="p-2 rounded cursor-pointer hover:bg-sky-100 transition"  
                v-for="item in topResults" 
                :key="item.app_id"
                @click="addResult(item)"
              >
                <img 
                  :src="getGameImage(item.app_id)" 
                  class="w-20 rounded"/>

                <span class="getGameReviewInfo(item.app_id)">{{ item.title}}</span>
              </li>
            </ul>
          </div>
        </div>
      </header>

    <!-- DASHBOARD -->
    <main class="grid grid-cols-[300px_1fr] gap-6">

      <!-- SIDEBAR / WISHLIST -->
      <aside class="bg-white rounded-xl shadow p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="font-semibold">Wishlist</h2>

          <button 
            class="text-sm text-sky-600 hover:underline"
            @click="toggleShow"
          >
            {{ showList ? "Hide" : "Show"}}
          </button>
        </div>

        <!-- SAVED LIST -->
        <GameList
          v-if="showList"
          :gameList="gameList"
          @showPriceHistory="showPriceHistory"
          @deleteGame="deleteGame"
        />
      </aside>

      <!-- MAIN CONTENT / CHART -->
      <section
        class="bg-white rounded-xl shadow p-6" 
        v-if="selectedGameId && priceHistory.length"
      >
        <!-- TITLE -->
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold">
            {{selectedGameTitle}} Price History
          </h2>

          <span class="text-sm text-gray-500">
            {{selectedPeriod}}
          </span>
        </div>

        <div class="border-b mb-4"></div>

        <!-- CHART -->
        <PriceChart
          v-if="selectedGameId && priceHistory.length"
          :data="priceHistory"
          :period="selectedPeriod"
          @closeChart="handleCloseChart"
          @selectPeriod="handleSetPeriod"
        />
      </section>

      <!-- EMPTY STATE -->
        <section 
          v-else
          class="bg-white rounded-xl shadow p-6 flex items-center justify-center text-gray-500"
        >
        Select a game from your wishlist to view price history 
        </section>

    </main>
          
    <!-- TOAST NOTIFICATIONS -->
    <div 
      v-if="notificationMessage"
      class="fixed bottom-6 right-6 bg-sky-500 text-white px-4 py-2 rounded-lg shadow-lg"
    > 
      {{notificationMessage}}
    </div>

    <footer>
    </footer>
  </div>
</template>
