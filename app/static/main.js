// Функция выбора города из подсказок
function selectCity(cityName) {
  document.querySelector('input[name="city"]').value = cityName;
  document.getElementById('suggestions').innerHTML = '';
  document.querySelector('form').submit();
}

// Скрытие подсказок при клике вне области
function hideSuggestionsOnClickOutside() {
  document.addEventListener('click', function(e) {
    if (!e.target.closest('#suggestions') && !e.target.matches('input[name="city"]')) {
      document.getElementById('suggestions').innerHTML = '';
    }
  });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
  const cityInput = document.querySelector('input[name="city"]');

  // Фокус на поле ввода при загрузке страницы
  if (cityInput && !cityInput.value) {
    cityInput.focus();
  }

  // Инициализируем обработчик кликов вне области
  hideSuggestionsOnClickOutside();
});