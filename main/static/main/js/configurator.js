// Function to add a new zone input
function addZone() {
    const zoneList = document.getElementById('zone-list');
    const zoneCount = zoneList.querySelectorAll('.zone-item').length; // Keep track of the zone count
    const newZoneItem = document.createElement('div');
    newZoneItem.classList.add('zone-item');
    newZoneItem.innerHTML = `
        <input type="text" name="zones[${zoneCount}][name]" placeholder="Введите имя зоны" required>
        <button type="button" class="remove-zone" onclick="removeZone(this)">Удалить</button>

        <div class="sector-list">
            <h4>Секторы</h4>
            <div class="sector-container">
                <!-- Dynamically added sector fields will go here -->
            </div>
            <button type="button" class="add-sector-btn" onclick="addSector(this, ${zoneCount})">Добавить сектор</button>
        </div>
    `;
    zoneList.appendChild(newZoneItem);
}

// Function to add a new sector input within a specific zone
function addSector(button, zoneIndex) {
    const sectorList = button.previousElementSibling; // sector-container
    const sectorCount = sectorList.querySelectorAll('.sector-item').length; // Track sectors per zone
    const newSectorItem = document.createElement('div');
    newSectorItem.classList.add('sector-item');
    newSectorItem.innerHTML = `
        <input type="text" name="zones[${zoneIndex}][sectors][${sectorCount}][name]" placeholder="Введите имя сектора" required>
        <input type="text" name="zones[${zoneIndex}][sectors][${sectorCount}][criteria]" placeholder="Операция/Критерий оценивания" required>
        <button type="button" class="remove-sector" onclick="removeSector(this)">Удалить</button>
    `;
    sectorList.appendChild(newSectorItem);
}

// Function to remove a zone input
function removeZone(button) {
    const zoneItem = button.parentElement;
    zoneItem.remove();
}

// Function to remove a sector input
function removeSector(button) {
    const sectorItem = button.parentElement;
    sectorItem.remove();
}
