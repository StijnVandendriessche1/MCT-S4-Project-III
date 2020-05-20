const fetchaData = async function(lat, lon) {
  return fetch(
    `http://api.openweathermap.org/data/2.5/forecast?lat=lat&lon=lon&appid=66654d8c2851633f35104f156f49ca9a&units=metric&lang=nl&cnt=1`
  )
    .then(r => r.json())
    .then(data => data);
};
// 2 Aan de hand van een longitude en latitude gaan we de yahoo wheater API ophalen.
let getAPI = async function(lat, lon) {
  // Eerst bouwen we onze url op
  // Met de fetch API proberen we de data op te halen.
  // Als dat gelukt is, gaan we naar onze showResult functie.
  try {
    const data = await fetchaData(lat, lon);
    showResult(data);
    console.log(data);
  } catch (error) {
    console.log(error);
  }
};