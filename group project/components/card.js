// Data for the cards (you can fetch this from an API or define it locally)
const cardsData = [
    { image: 'image.png', title: 'Project Title 1', manager: 'Project Manager 1' },
    { image: 'image.png', title: 'Project Title 2', manager: 'Project Manager 2' },
    { image: 'image.png', title: 'Project Title 3', manager: 'Project Manager 3' },
    { image: 'image.png', title: 'Project Title 4', manager: 'Project Manager 4' },
    { image: 'image.png', title: 'Project Title 5', manager: 'Project Manager 5' },
    { image: 'image.png', title: 'Project Title 6', manager: 'Project Manager 6' },
    { image: 'image.png', title: 'Project Title 7', manager: 'Project Manager 7' },
    
  ];
  
  // Function to create a card element
  function createCard(cardData) {
    const card = document.createElement('div');
    card.classList.add('card');
  
    const cardContent = document.createElement('div');
    cardContent.classList.add('card-content');
  
    const imageContainer = document.createElement('div');
    imageContainer.classList.add('image-container');
  
    const cardImage = document.createElement('img');
    cardImage.src = cardData.image;
    cardImage.alt = 'Card Image';
    cardImage.classList.add('card-image');
  
    const detailsContainer = document.createElement('div');
    detailsContainer.classList.add('details-container');
  
    const projectTitle = document.createElement('div');
    projectTitle.classList.add('project_title');
    projectTitle.textContent = cardData.title;
  
    const projectManager = document.createElement('div');
    projectManager.classList.add('pm');
    projectManager.textContent = cardData.manager;
  
    const editButton = document.createElement('div');
    editButton.classList.add('edit');
    const editSpan = document.createElement('span');
    editSpan.textContent = 'Edit';
    editButton.appendChild(editSpan);
    
  editButton.addEventListener('click', function() {
      window.location.href = 'edit_page.html';});

  


  // Add click event listener to the card to redirect to another page
  card.addEventListener('click', function() {
    window.location.href = 'projectview.html'; // Replace 'another_page.html' with your desired URL
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
function renderCardsInRow() {
  const cardContainer = document.getElementById('cardContainer');
  cardsData.forEach((cardData) => {
    const cardElement = createCard(cardData);
    cardContainer.appendChild(cardElement);
  });
}
  
  // Function to render cards in a row
  function renderCardsInRow() {
    const cardContainer = document.getElementById('cardContainer');
    cardsData.forEach((cardData) => {
      const cardElement = createCard(cardData);
      cardContainer.appendChild(cardElement);
    });
  }

  // Call the renderCardsInRow function to display the cards in a row
  renderCardsInRow();
