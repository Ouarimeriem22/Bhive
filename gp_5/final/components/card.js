// Data for the cards (you can fetch this from an API or define it locally)

// Function to read from the database and create card elements
document.addEventListener('DOMContentLoaded', function() {
  // Function to create a card element
  function createCard(cardData) {
      const card = document.createElement('div');
      card.classList.add('card');

      const cardContent = document.createElement('div');
      cardContent.classList.add('card-content');

      const imageContainer = document.createElement('div');
      imageContainer.classList.add('image-container');

      const cardImage = document.createElement('img');
      cardImage.src = 'image.png'; 
      cardImage.alt = 'Card Image';
      cardImage.classList.add('card-image');

      const detailsContainer = document.createElement('div');
      detailsContainer.classList.add('details-container');

      const projectTitle = document.createElement('div');
      projectTitle.classList.add('project_title');
      projectTitle.textContent = cardData.p_Name;

      const projectManager = document.createElement('div');
      projectManager.classList.add('pm');
      projectManager.textContent = cardData.PM_name;

      const editButton = document.createElement('div');
      editButton.classList.add('edit');
      const editSpan = document.createElement('span');
      editSpan.textContent = 'Edit';
      editButton.appendChild(editSpan);


      card.addEventListener('click', function() {
        // Extract the project name from the card
        const projectName = cardData.p_Name;
        // Fetch project ID from server using the project name
        fetch(`http://localhost:5050/get_project_id?project_name=${projectName}`)
            .then(response => response.json())
            .then(data => {
                // Check if the project ID was retrieved successfully
                if (data.status === 200 && data.project_id) {
                    // Add project ID to session storage
                    sessionStorage.setItem('projectID', data.project_id);
                    // Redirect to project view page
                    
                    window.location.href = `projectview.html`;
                } else {
                    console.error('Error retrieving project ID:', data.message);
                }
            })
            .catch(error => {
                console.error('Error fetching project ID:', error);
            });
    });

    editButton.addEventListener('click', function(event) {
        // Redirect to edit project page
        window.location.href = 'project_des.html';
    });

      imageContainer.appendChild(cardImage);
      detailsContainer.appendChild(projectTitle);
      detailsContainer.appendChild(projectManager);
      detailsContainer.appendChild(editButton);

      cardContent.appendChild(imageContainer);
      cardContent.appendChild(detailsContainer);

      card.appendChild(cardContent);

      return card;
  }

  // Function to render cards in a row
  function renderCardsInRow(cardsData) {
      const cardContainer = document.getElementById('cardContainer');
      if (cardContainer) {
          cardsData.forEach((cardData) => {
              const cardElement = createCard(cardData);
              cardContainer.appendChild(cardElement);
          });
      } else {
          console.error('Card container element not found.');
      }
  }

  // Fetch project data from the server and render the cards
  fetch('http://localhost:5050/get_projects')
      .then(response => response.json())
      .then(data => {
          const projects = data.projects;
          renderCardsInRow(projects);
      })
      .catch(error => {
          console.error('Error fetching project data:', error);
      });
});
