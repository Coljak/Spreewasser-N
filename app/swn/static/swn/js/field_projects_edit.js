import { endpoint, chartDiv, crop, getChart } from "./chart_page.js";

const getSoilData = document.getElementById("getSoilData");

getSoilData.addEventListener("click", function () {
    console.log("CurrentUserField: ", userFieldId);
    let soilDataUrl = `/login/Dashboard/get-soil-data/${userFieldId}`;
    fetch(soilDataUrl).then((response) => response.json()).then((data) => {
        console.log("Soil Data: ", data);
    });
});

const btnModalCal = document.getElementById("btnModalCal");

btnModalCal.addEventListener("click", function () {
    getChart();
    chartCard.classList.remove("d-none");
  });