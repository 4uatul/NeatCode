// Sample code for Try Me button
export const sampleCode = `function calculateTotal(items) {
    var total = 0;
    for (var i = 0; i < items.length; i++) {
        total = total + items[i].price;
    }
    return total;
}

var items = [
    {name: 'Apple', price: 1.50},
    {name: 'Banana', price: 0.75},
    {name: 'Orange', price: 2.00}
];

console.log('Total: $' + calculateTotal(items));`;

// Simple simulation of refactoring
export const simulateRefactoring = (code, language) => {
  const languageName = language === 'auto' ? 'auto-detected' : language;
  
  return `// Refactored code (${languageName})
// This is a simulation - a real tool would provide actual refactoring

${code}

// Refactoring completed
// Code has been optimized for readability and maintainability`;
};