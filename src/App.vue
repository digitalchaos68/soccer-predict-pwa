<script setup>
import { onMounted, ref } from 'vue';
import { fetchPredictions } from './lib/predictions';

const predictions = ref([]);
const history = ref([]);
const stats = ref({ correct: 0, incorrect: 0, accuracy: 0 });
const activeTab = ref('upcoming');
const darkMode = ref(false);

onMounted(async () => {
  const allPredictions = await fetchPredictions();
  
  // Split into upcoming and history
  const now = new Date();
  const twoWeeksFromNow = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000);
  
  predictions.value = allPredictions.filter(p => new Date(p.date) > now);
  history.value = allPredictions.filter(p => p.actual_result && new Date(p.date) <= now);

  // Calculate stats
  stats.value = {
    correct: history.value.filter(p => p.correct).length,
    incorrect: history.value.filter(p => !p.correct).length,
    accuracy: history.value.length > 0 ? Math.round((history.value.filter(p => p.correct).length / history.value.length) * 100) : 0
  };
});

function toggleDarkMode() {
  darkMode.value = !darkMode.value;
  document.documentElement.classList.toggle('dark', darkMode.value);
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <img src="/logo.png" alt="SoccerPredict" class="w-8 h-8" />
          <h1 class="text-2xl font-bold text-blue-600 dark:text-blue-400">SoccerPredict</h1>
        </div>
        <button 
          @click="toggleDarkMode"
          class="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          <svg v-if="!darkMode" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-300" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707-.707a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Tabs -->
    <div class="max-w-4xl mx-auto px-4 py-4">
      <div class="flex space-x-1 bg-gray-200 dark:bg-gray-700 p-1 rounded-lg mb-6">
        <button 
          @click="activeTab = 'upcoming'"
          :class="{
            'px-4 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400': activeTab === 'upcoming',
            'px-4 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600': activeTab !== 'upcoming'
          }"
        >
          Upcoming
        </button>
        <button 
          @click="activeTab = 'history'"
          :class="{
            'px-4 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400': activeTab === 'history',
            'px-4 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600': activeTab !== 'history'
          }"
        >
          History
        </button>
        <button 
          @click="activeTab = 'stats'"
          :class="{
            'px-4 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400': activeTab === 'stats',
            'px-4 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600': activeTab !== 'stats'
          }"
        >
          Stats
        </button>
      </div>

      <!-- Content -->
      <div class="space-y-6">
        <!-- Upcoming Predictions -->
        <div v-if="activeTab === 'upcoming'" class="space-y-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Upcoming Predictions (Next 2 Weeks)</h2>
          <div v-for="p in predictions" :key="p.id" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
              <div>
                <p class="font-medium">{{ p.home_team }} vs {{ p.away_team }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ p.date }}</p>
              </div>
              <div class="text-right">
                <div class="text-sm text-gray-500 dark:text-gray-400">Confidence</div>
                <div class="text-lg font-semibold text-blue-600 dark:text-blue-400">{{ p.confidence }}%</div>
              </div>
            </div>
            <div class="mt-3">
              <div class="flex items-center space-x-2">
                <span class="text-sm font-medium">Prediction:</span>
                <span class="text-sm font-medium text-green-600 dark:text-green-400">{{ p.prediction }}</span>
                <span class="text-sm text-gray-500 dark:text-gray-400">→ {{ p.score_pred }}</span>
              </div>
            </div>
            <!-- Confidence bar -->
            <div class="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-400 dark:to-blue-500 transition-all duration-300"
                :style="{ width: `${p.confidence}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Prediction History -->
        <div v-else-if="activeTab === 'history'" class="space-y-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Prediction History (Last 2 Weeks)</h2>
          <div v-for="p in history" :key="p.id" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
              <div>
                <p class="font-medium">{{ p.home_team }} vs {{ p.away_team }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ p.date }}</p>
              </div>
              <div class="text-right">
                <div class="text-sm text-gray-500 dark:text-gray-400">Confidence</div>
                <div class="text-lg font-semibold text-blue-600 dark:text-blue-400">{{ p.confidence }}%</div>
              </div>
            </div>
            <div class="mt-3">
              <div class="flex items-center space-x-2">
                <span class="text-sm font-medium">Prediction:</span>
                <span class="text-sm font-medium text-green-600 dark:text-green-400">{{ p.prediction }}</span>
                <span class="text-sm text-gray-500 dark:text-gray-400">→ {{ p.score_pred }}</span>
              </div>
              <div class="mt-1">
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium">Actual:</span>
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ p.score_actual }}</span>
                </div>
              </div>
              <div class="mt-1 flex items-center space-x-2">
                <span v-if="p.correct" class="text-green-600 dark:text-green-400">✅ Correct</span>
                <span v-else class="text-red-600 dark:text-red-400">❌ Incorrect</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div v-else-if="activeTab === 'stats'" class="space-y-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Prediction Performance</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Accuracy</h3>
              <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.accuracy }}%</div>
              <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Overall Accuracy Rate</div>
            </div>
            
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Performance</h3>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">Correct</span>
                  <span class="font-medium">{{ stats.correct }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">Incorrect</span>
                  <span class="font-medium">{{ stats.incorrect }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Trends</h3>
            <ul class="space-y-2">
              <li class="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span>3 correct home wins in a row</span>
              </li>
              <li class="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <span>2 missed draws last week</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="mt-12 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-6">
      <div class="max-w-4xl mx-auto px-4 text-center text-sm text-gray-500 dark:text-gray-400">
        <p>Add to Home Screen for best experience</p>
      </div>
    </footer>
  </div>
</template>