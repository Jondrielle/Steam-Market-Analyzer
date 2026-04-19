<script setup>
import { ref, onMounted, onBeforeUnmount,onUnmounted,computed} from 'vue'
import axios from 'axios'
import GameList from './components/GameList.vue'
import PriceChart from './components/PriceChart.vue'
import SearchFunction from './components/SearchFunction.vue'
import { ChartBarSquareIcon, MagnifyingGlassIcon,TrashIcon} from '@heroicons/vue/24/outline'
import notificationAudio from './assets/Notification.wav'


let interval
let notificationTimer = null

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
const notificationSound = ref(null)
const reviewSummary = ref({
  total_reviews:0,
  positive:0,
  negative:0
})
const loading = ref(false)


const selectedGameTitle = computed(()=>{
  const game = gameList.value.find(g => g.app_id === selectedGameId.value)
  return game ? game.title : ""
})

async function getReviews(appId){
  console.log("Game id is:", appId)
  try{
    const response = await axios.get(`http://localhost:8000/reviews/${appId}`)

    reviewSummary.value = response.data.query_summary
    console.log("Review:", reviewSummary.value)

  }catch(error){
    console.error("Failed to fetch reviews",error)
    console.log(error.response)
  }
}

// TRIGGER NOTIFICATIONS
function triggerNotification(message){
  notificationMessage.value = message

  if(notificationSound.value){
    notificationSound.value.volume = 0.3
    notificationSound.value.currentTime = 0
    notificationSound.value.play()
  }

  clearTimeout(notificationTimer)

  notificationTimer = setTimeout(()=>{
    notificationMessage.value = null
  },2000)
}

// REQUEST RESULTS
async function getResults() {
  try {
    if(searchName.value == ''){ 
      triggerNotification("Please enter a game name to search")
      return
    }

    const response = await axios.get('http://localhost:8000/find', {
      params: { title: searchName.value }
    })

    console.log('Response:', response.data)  
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
      triggerNotification(`${item.title} already in your wishlist`)
      return
    }

    await axios.post('http://localhost:8000/add', item)
    gameList.value.push(item)
    topResults.value = []
    showResults.value = false
    searchName.value = ""

    triggerNotification(`${item.title} was added`)

    await displayList()
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


    triggerNotification(`${item.title} was deleted`)

    await displayList()
  } catch (error) {
    console.error('Delete Failed', error)
  }
}

// GAME LIST 
async function displayList() {
  try{
    const response = await axios.get('http://localhost:8000/list')
    gameList.value = response.data || []
  }catch(err){
    console.error("Failed to load wishlist", err)
  }
}

// REQUEST PRICE TREND 
async function showPriceHistory(gameId){
  console.log("Game Selected:", gameId)
  selectedGameId.value = gameId
  try {
    loading.value = true
    const response = await axios.get(`http://localhost:8000/games/${gameId}/price-history`, {
      params: { period: selectedPeriod.value }
    });

    console.log("FULL RESPONSE:", response.data)
    priceHistory.value = response.data.prices
    console.log("APP priceHistory:", priceHistory.value)
    loading.value = false 
  } catch (err) {
    console.error("Failed to fetch price history", err);
  }

  await getReviews(gameId)
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
  console.log("App ID:", appId )
  return `https://cdn.cloudflare.steamstatic.com/steam/apps/${appId}/header.jpg` || `https://cdn.akamai.steamstatic.com/steam/apps/${appId}/capsule_616x353.jpg`
}

async function getGameReviewInfo(appId){
  try{
    const response = await axios.get("http://store.steampowered.com/appreviews/<${appId}>?json=1")

    console.log('Response:', response)
  }catch(e){
    console.log('Error:',e)
  }
}

async function updatePrices(){
  try{
    const response = await axios.post("http://localhost:8000/update-prices")
    await displayList()

    // await showPriceHistory(selectGameId.value)
    console.log("Response:", response.data)
  }catch(e){
    console.log('Error:',e)
  }
}


onMounted( async ()=> {
  await displayList()

  interval = setInterval(async ()=> {
    if(selectedGameId.value){
      await showPriceHistory(selectedGameId.value)
    }
  }, 10000)
  
  document.addEventListener('click',handleClickOutside)
})

onBeforeUnmount(()=> {
  document.removeEventListener('click',handleClickOutside)
})

onUnmounted(() =>{
  clearInterval(interval)
})


</script>

<template>
  <div class="min-h-screen flex justify-center items-center">

    <div class="bg-gray-100 rounded-xl w-full max-w-5xl px-4 pt-28 pb-6 space-y-8">

      <!-- HEADER -->
      <header class="bg-white rounded-xl shadow-md p-6 sticky top-0 z-20"> 

      <h1 class="text-2xl font-bold text-gray-800">Steam Price Tracker</h1>

      <!-- SEARCH BAR -->
      <div class="flex gap-2">
        <input 
          v-model="searchName" 
          placeholder="Enter game name"
          @keyup.enter="getResults"
          class="border rounded-xl px-4 py-2 flex-1 focus:outline-none focus:ring-2 focus:ring-sky-400"
        />
          <button 
            class="flex items-center gap-2 px-4 bg-sky-500 text-white rounded-xl hover:bg-sky-600 active:scale-95 transition-all duration-150 shadow-sm" 
            @click="getResults">
            <MagnifyingGlassIcon 
              class="size-5"/>
          Search  
          </button>
      </div>

      <!-- SEARCH RESULTS -->
      <button @click="updatePrices">Update Prices</button>
      <div 
        ref="resultsBox" 
        v-if="showResults && topResults.length"
        class="absolute top-full mt-2 w-full bg-white rounded-xl shadow-sm border border-gray-200 z-30 max-h-80 overflow-y-auto"
      >
            <ul class="grid grid-cols-2 gap-3">
              <li 
                class="p-3 rounded-lg cursor-pointer hover:bg-sky-100 transition transform hover:scale-105 active:scale-95 flex items-center gap-3"  
                v-for="item in topResults" 
                :key="item.app_id"
                @click="addResult(item)"
              >
              <img 
                :src="item.image_url" 
                class="w-16 rounded"/>

                <span class="text-sm font-medium text-gray-800"
                @click.stop="getGameReviewInfo(item.app_id)">{{ item.title}}
                </span>
              </li>
            </ul>
        </div>
      </header>

      <div class="p-2"></div>

      <!-- DASHBOARD -->
      <main class="grid grid-cols-2 md:grid-cols-[290px_1fr] gap-6 items-start">

        <!-- SIDEBAR / WISHLIST -->
        <aside class="bg-white rounded-xl shadow-md p-4 h-fit">

          <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-semibold tracking-tight">Wishlist</h2>

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

        <!-- MAIN CONTENT -->  
          <section 
          class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6"
          v-if="selectedGameId && priceHistory.length">

            <!-- TITLE -->
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold text-gray-800">
                {{selectedGameTitle}} Price Chart
              </h2>

              <span class="text-sm text-gray-500 capitalize">
                ({{selectedPeriod}})
              </span>
            </div>

            <div class="border-b border-gray-200"></div>

            <!-- CHART -->
            <div v-if="loading" class="space-y-4 animate-pulse">

              <div class="h-6 bg-gray-300 rounded w-1/3"></div>

              <div class="h-64 bg-gray-300 rounded-xl"></div>

              <div class="space-y-2">
                <div class="h-4 bg-gray-300 rounded w-1/2"></div>
                <div class="h-4 bg-gray-300 rounded w-1/3"></div>
              </div>
            </div>

            <PriceChart
              v-else-if="selectedGameId && priceHistory.length && !loading"
              :data="priceHistory"
              :period="selectedPeriod"
              @closeChart="handleCloseChart"
              @selectPeriod="handleSetPeriod"
              class="text-gray-500"
            />

            <div v-else-if="selectedGameId"> No price history available </div>
            
            <div class="border-b border-gray-200"></div>

          <!-- REVIEWS -->
          <div v-if="reviewSummary.total_reviews > 0">
            <h5 class="text-lg font-bold mb-2 text-gray-800">{{reviewSummary.review_score_desc}}</h5>

            <p class="font-semibold text-base mb-2"> {{((reviewSummary.total_positive/reviewSummary.total_reviews)*100).toFixed(0)}}% Positive</p>

            <div class="h-2 rounded-full bg-gray-200 w-full">
              <div 
              class="h-2 rounded-full bg-green-500"
              :style="{ width:((reviewSummary.total_positive /reviewSummary.total_reviews) * 100) + '%' }"
              >
              </div>
            </div>

            <p class="text-green-600 mt-2 text-sm">{{reviewSummary.total_positive.toLocaleString()}} Positive Reviews</p>
            
            <p class="text-red-600 text-sm">{{reviewSummary.total_negative.toLocaleString()}} Negative Reviews</p>

          </div>

          <div v-else-if="reviewSummary.total_reviews == 0" class="text-gray-500"> No Available Reviews</div>

        </section>

          <!-- EMPTY STATE -->
          <section 
            v-else
            class="bg-white rounded-xl shadow-md border border-gray-200 top-20 p-6 flex flex-col justify-center text-gray-500 text-center min-h-[400px] top-30"
          >
          Select a game from your wishlist to view price history 
          </section>
    </main>
          
    <!-- TOAST NOTIFICATIONS -->
    <div 
      v-if="notificationMessage"
      class="fixed bottom-6 right-6 bg-gray-900/90 backdrop-blur text-white px-5 py-3 rounded-xl shadow-lg"
    > 
      {{notificationMessage}}
    </div>
    <audio ref="notificationSound">
      <source src="./assets/Notification.wav" type="audio/wav" />
    </audio>

    </div> <!-- 2ND OUTER MOST DIV -->
  </div> <!-- 1ST OUTER MOST DIV -->
</template>



                  



      



 