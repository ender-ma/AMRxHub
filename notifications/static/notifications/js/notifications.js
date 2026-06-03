document.addEventListener('DOMContentLoaded', function() {
    // Notification bell and dropdown elements
    const notificationBell = document.querySelector('.notification-bell');
    const notificationCount = document.querySelector('.notification-count');
    const notificationDropdownContainer = document.getElementById('notification-dropdown-container');
    
    // Update notification count
    function updateNotificationCount() {
        fetch('/notifications/count/')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    notificationCount.textContent = data.count > 99 ? '99+' : data.count;
                    notificationCount.style.display = 'flex';
                } else {
                    notificationCount.style.display = 'none';
                }
            })
            .catch(error => console.error('Error fetching notification count:', error));
    }
    
    // Load notifications into dropdown
    function loadNotifications() {
        fetch('/notifications/list/?format=html&limit=5')
            .then(response => response.text())
            .then(html => {
                notificationDropdownContainer.innerHTML = html;
                setupNotificationItemHandlers();
            })
            .catch(error => console.error('Error loading notifications:', error));
    }
    
    // Mark notification as read
    function markAsRead(notificationId) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/notifications/mark-read/${notificationId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotificationCount();
            }
        })
        .catch(error => console.error('Error marking notification as read:', error));
    }
    
    // Mark all notifications as read
    function markAllAsRead() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/notifications/mark-all-read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotificationCount();
                loadNotifications();
            }
        })
        .catch(error => console.error('Error marking all notifications as read:', error));
    }
    
    // Setup event handlers for notification items
    function setupNotificationItemHandlers() {
        // Mark as read when clicked
        document.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', function() {
                const notificationId = this.dataset.id;
                markAsRead(notificationId);
                this.classList.remove('unread');
            });
        });
        
        // Mark all as read button
        const markAllReadBtn = document.getElementById('mark-all-read');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                markAllAsRead();
            });
        }
    }
    
    // Toggle notification dropdown
    if (notificationBell) {
        notificationBell.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const isActive = notificationDropdownContainer.classList.contains('active');
            
            if (!isActive) {
                loadNotifications();
            }
            
            notificationDropdownContainer.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!notificationDropdownContainer.contains(e.target) && 
                !notificationBell.contains(e.target)) {
                notificationDropdownContainer.classList.remove('active');
            }
        });
    }
    
    // Initialize
    updateNotificationCount();
    
    // Periodically update notification count (every 30 seconds)
    setInterval(updateNotificationCount, 30000);
});