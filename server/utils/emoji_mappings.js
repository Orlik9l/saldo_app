// Category-specific emoji mappings
export const categoryEmojis = {
    // Income categories
    'Salary': '💰',
    'Dividends': '💵',
    'Rental income': '🏘️',
    'Freelance': '💻',
    'Business': '💼',
    'Interest': '🏦',
    'Gifts received': '🎀',
    'Refunds': '↩️',
    'Other income': '💸',

    // Expense categories
    'Groceries': '🛒',
    'Eating out': '🍽️',
    'Transport': '🚗',
    'Entertainment': '🎮',
    'Shopping': '🛍️',
    'Health': '⚕️',
    'Education': '📚',
    'Bills': '📄',
    'Rent': '🏠',
    'Travel': '✈️',
    'Gifts': '🎁',
    'Sports': '⚽',
    'Beauty': '💅',
    'Pets': '🐾',
    'Taxi': '🚕',
    'Coffee': '☕',
    'Alcohol': '🍺',
    'Clothes': '👕',
    'Internet': '🌐',
    'Phone': '📱',
    'Utilities': '💡',
    'Insurance': '🛡️',
    'Car': '🚙',
    'Parking': '🅿️',
    'Pharmacy': '💊',
    'Doctor': '👨‍⚕️',
    'Gym': '🏋️',
    'Movies': '🎬',
    'Music': '🎵',
    'Books': '📚',
    'Software': '💻',
    'Charity': '🤝',
    'Investment': '📈',
    'Other expenses': '📋',

    // Add more categories as needed
};

// Account type emoji mappings
export const typeEmojis = {
    'INCOME': '💵',
    'EXPENSES': '💳',
    'ASSETS': '🏦',
    'LIABILITIES': '📊',
    'DEFAULT': '📝'  // default fallback
};

/**
 * Get the appropriate emoji for a category
 * @param {Object} category - The category object containing name and type
 * @returns {string} - The emoji for the category
 */
export function getCategoryEmoji(category) {
    // Try to find a specific emoji for the category name
    if (category.name in categoryEmojis) {
        return categoryEmojis[category.name];
    }

    // Fallback to account type emoji
    return typeEmojis[category.type] || typeEmojis.DEFAULT;
} 