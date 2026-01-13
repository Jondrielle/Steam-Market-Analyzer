<script setup>
import { ref } from 'vue';
import axios from 'axios';

// Use ref to create a reactive variable for search input
const searchName = ref('');
const selectedItem = ref('');
const topResults = ref({});

// Define the function to get results
async function getResults() {
  try {
    // Send the searchName in the request body
    // Correct way to make a GET request
    const response = await axios.get(`http://localhost:8000/find?title=${searchName.value}`);
    console.log(response);
    topResults.value = response.data
  } catch (error) {
    console.error('Error fetching results:', error);
  }
}

//Display list of results

// Add result to list
async function addResult(item){
  try{
    const response = await axios.post('http://localhost:8000/add', {
      title: item.Title,
      app_id: item.AppID,
      original_price: item["Original Price"],
      discount: item.Discount,
      final_price: item["Final Price"]
    });
    console.log("Game added ", item.Title)
    clearTopResults()
  }catch(error){
    console.error('Error adding game to list', error);
  }
}

// Clear top results list 
function clearTopResults(){
  topResults.value = []
}
// Delete game from list

</script>



<template>
  <div>
    <!-- Input field for search name -->
    <input v-model="searchName" type="text" placeholder="Enter game name" />

    <!-- Button to trigger the search -->
    <button @click="getResults">Search</button>
  </div>
  <div v-if="topResults.length > 0">
    <h3>Top Results:</h3>
      <ul>
        <li v-for="item in topResults" :key="item.Title">
          <button @click="addResult(item)">{{ item.Title }}</button>
        </li>
      </ul>
  </div>
</template>

