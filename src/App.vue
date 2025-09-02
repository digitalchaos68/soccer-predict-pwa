<script setup>
import { onMounted, ref } from 'vue';
import { fetchPredictions } from './lib/predictions';

const predictions = ref([]);
const loading = ref(true);

onMounted(async () => {
  predictions.value = await fetchPredictions();
  loading.value = false;
});
</script>

<template>
  <div class="p-4 max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">⚽ AI Football Predictions</h1>

    <div v-if="loading">Loading predictions...</div>

    <div v-else class="space-y-4">
      <div 
        v-for="p in predictions" 
        :key="p.id"
        class="border p-4 rounded-lg hover:shadow-md transition"
        :class="{
          'border-green-500': p.confidence > 65,
          'border-yellow-500': p.confidence >= 50 && p.confidence <= 65,
          'border-red-500': p.confidence < 50
        }"
      >
        <div class="flex justify-between text-sm text-gray-500">
          {{ p.league }} • {{ p.date }}
        </div>
        <div class="font-medium mt-1">
          {{ p.home_team }} vs {{ p.away_team }}
        </div>
        <div class="text-sm mt-1">
          🎯 <strong>{{ p.prediction }}</strong> → {{ p.score_pred }} 
          <span class="text-green-600">({{ p.confidence }}%)</span>
        </div>
      </div>
    </div>
  </div>
</template>