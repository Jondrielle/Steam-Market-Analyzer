<script setup>
import { defineEmits, defineProps } from 'vue'
import {TrashIcon, ChartBarSquareIcon} from '@heroicons/vue/24/outline'
const props = defineProps({
  gameList: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['showPriceHistory', 'deleteGame'])

function emitShowPriceHistory(game){
  emit('showPriceHistory', game.app_id)
}

function emitDeleteGame(game){
  emit('deleteGame', game)
}
</script>

<template>
  <div 
  v-if="props.gameList.length" 
  class="border-3 border-red-300">
    <ul>
      <li
        v-for="game in props.gameList"
        :key="game.app_id"
        class="flex items-center justify-between py-2 hover:bg-gray-300"
      >
        <!-- Title -->
        <h2 class="text-lg font-medium">
          {{ game.title }}
        </h2>

        <!-- Icons -->
        <div class="flex items-center gap-3">
          <button 
            @click="emitShowPriceHistory(game)">
            <ChartBarSquareIcon class="w-5 h-5" />
          </button>

          <button 
            @click="emitDeleteGame(game)">
            <TrashIcon class="w-5 h-5" />
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>
