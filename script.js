document.addEventListener("DOMContentLoaded", function() {
  // Function to add list items to #listContainer
  function addListItem(name, total, max, min) {
	const listItem = document.createElement("li");
	listItem.innerHTML = `
	<a href="stat/?stat=${name}">
	<strong class=stathead >${name}</strong>
	<div class="total"><div>
	
		Total: ${total}
	</div></div>
	<div class="players">
		<div class="minimax">
			<span>Max: ${max.amount}</span>
			<div class=inline>
				${max.players.map(player => `<span>${player}</span> `).join("")}
			</div> 
		</div>
		<div class="minimax">
			<span>Min: ${min.amount}</span>
			<div  class=inline>
			${min.players.map(player => `<span>${player}</span> `).join("")}
			</div> 
		</div> 
	</div>
	</a>
	`;
	listContainer.appendChild(listItem);
  }

  const filterInput = document.getElementById("searchInput");
  const listContainer = document.getElementById("listContainer");

  // Function to filter the list items based on the input value
  function filterListItems() {
	const filterValue = filterInput.value.toLowerCase();
	const listItems = listContainer.getElementsByTagName("li");

	for (const listItem of listItems) {
	  const name = listItem.querySelector("strong").textContent.toLowerCase();
	  const players = listItem.querySelectorAll("li");

	  let foundMatch = name.includes(filterValue);

	  players.forEach(player => {
		if (player.textContent.toLowerCase().includes(filterValue)) {
		  foundMatch = true;
		}
	  });

	  listItem.style.display = foundMatch ? "block" : "none";
	}
  }
  const cacheKey = "cachedJSONData";
function loadJSONData() {
        return new Promise((resolve, reject) => {
          // Check if the JSON data is already cached
          const cachedData = localStorage.getItem(cacheKey);

          if (cachedData) {
            // If data is cached, parse and resolve the promise
            const jsonData = JSON.parse(cachedData);
            resolve(jsonData);
          } else {
            // If data is not cached, make a fetch request and cache the data
            fetch("leaderboard.json")
              .then(response => response.json())
              .then(data => {
                // Cache the data in localStorage
                localStorage.setItem(cacheKey, JSON.stringify(data));
                resolve(data);
              })
              .catch(error => reject(error));
          }
        });
      }

      // Load the JSON data and add list items asynchronously
      loadJSONData()
        .then(data => {
          for (const entry of data) {
            addListItem(entry.name, entry.total, entry.max, entry.min);
          }
        })
        .catch(error => console.error("Error loading JSON data:", error));
    });
