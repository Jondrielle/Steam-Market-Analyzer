<script setup>
import { ref, watch, onMounted } from 'vue'
import { Chart } from 'chart.js/auto'
import { XCircleIcon} from '@heroicons/vue/24/outline'

const props = defineProps({
  data: {
    type: Array,
    default: () => []   // ← IMPORTANT
  },
  period: String
})

const emit = defineEmits(["closeChart","selectPeriod"])

function closeChartCanvas(){
  emit("closeChart")
}

function selectHistoryPeriod(period){
  emit("selectPeriod",period)
}

const canvasRef = ref(null)
let chart = null

function renderChart() {
  console.log("Rendering chart with:", props.data)

  if (!props.data || !props.data.length || !canvasRef.value) return

  const labels = props.data.map(p =>
    new Date(p.date).toLocaleDateString()
  )
  const prices = props.data.map(p => p.final_price)

  if (chart) {
    chart.destroy()
  }

  chart = new Chart(canvasRef.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Final Price ($)',
          data: prices,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  })
}

onMounted(() => {
  console.log("PriceChart mounted")
  renderChart()
})

watch(
  () => props.data,
  () => {
    renderChart()
  },
  { deep: true }
)
</script>

<template>
  <div class="flex flex-cols-2 gap-10">
    <div class="relative inline-block">
      <canvas
        ref="canvasRef"
        class="block"
      ></canvas>
      <button
        class="absolute -top-2 -right-10 bg-white rounded-full p-1 shadow hover:bg-gray-100"
      >
      </button>
    </div>
    <div class="flex flex-col gap-5">
      <button 
        @click="selectHistoryPeriod('daily')" 
        :class="period === 'daily'
        ? 'bg-white px-4 py-2 rounded-md shadow'
        : 'px-4 py-2 text-gray-900'">Daily</button>
      <button 
        @click="selectHistoryPeriod('monthly')" 
          :class="period === 'monthly'
          ? 'bg-white px-4 py-2 rounded-md shadow'
          : 'px-4 py-2 text-gray-900'">Monthly</button>
      <button
        @click="selectHistoryPeriod('yearly')" 
        :class="period === 'yearly'
        ? 'bg-white px-4 py-2 rounded-md shadow'
        : 'px-4 py-2 text-gray-900'">Yearly</button>
    </div>
    <div>
      <XCircleIcon 
        class="w-6 h-6" 
        @click="closeChartCanvas"
      />
    </div>
  </div>
</template>


