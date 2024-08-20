// Function to add a new zone input
function addZone() {
    const zoneList = document.getElementById('zone-list');
    const newZoneItem = document.createElement('div');
    newZoneItem.classList.add('zone-item');
    newZoneItem.innerHTML = `
        <input type="text" name="zones[]" placeholder="Введите имя объекта" required>
        <button type="button" class="remove-zone" onclick="removeZone(this)">Удалить</button>
    `;
    zoneList.appendChild(newZoneItem);
}

// Function to remove a zone input
function removeZone(button) {
    const zoneItem = button.parentElement;
    zoneItem.remove();
}