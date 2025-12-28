<script setup>
import { ref } from 'vue';
import axios from 'axios';

// Use ref to create a reactive variable for search input
const searchName = ref('');
const selectedItem = ref('');

// Define the function to get results
async function getResults() {
  try {
    // Send the searchName in the request body
    // Correct way to make a GET request
    const response = await axios.get(`http://localhost:8000/find?title=${searchName.value}`);
    console.log(response);
  } catch (error) {
    console.error('Error fetching results:', error);
  }
}

//Display list of results

// Add result to list
async function addResult(){
  try{
    const response = await axios.post('http://localhost:8000/add', {title: searchName.value});
    console.log(response)
  }catch(error){
    console.error('Error adding game to list', error);
  }
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
</template>

