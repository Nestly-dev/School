[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=21675922)
## Guided Learning Activity: African Marketplace Manager

### Canvas Module Overview

**Duration:** 6-10 hours  
**Format:** Pair Programming  
**Submission:** Via GitHub Classroom  

---

## Project Context

You'll build a **Digital Marketplace Management System** for African entrepreneurs managing multiple vendor stalls across markets in cities like Kigali, Lagos, or Nairobi. This system will help market administrators track vendors, products, sales, and inventory using ES6 classes and advanced data manipulation techniques.

This activity integrates your knowledge of:
- ES6 classes and inheritance
- Array and object manipulation (map, filter, reduce, destructuring)
- Redis (for caching frequently accessed data)
- Database operations (for persistence)
- i18n (for multi-language support in East Africa)

---

## Pair Programming Guidelines

### Roles
- **Driver:** Types the code
- **Navigator:** Reviews, suggests, thinks ahead
- **Switch every 30 minutes** or after completing each challenge

### Collaboration Tips
- Discuss approach before coding
- Explain your reasoning
- Ask questions when unclear
- Both partners should understand all code written
- Use comments to document decisions

### Communication
- Use clear variable names you both agree on
- Discuss trade-offs
- Review code together before moving to next challenge

---

## Learning Objectives

By completing this activity, you will:
1. Design and implement class hierarchies using ES6 syntax
2. Apply inheritance and polymorphism to real-world scenarios
3. Manipulate complex data structures using ES6 methods
4. Integrate caching strategies with Redis
5. Build a complete, functional application architecture
6. Practice collaborative coding techniques

---

## GitHub Classroom Setup

### Repository Structure
```
marketplace-manager/
├── src/
│   ├── models/
│   │   ├── Vendor.js
│   │   ├── Product.js
│   │   ├── DigitalProduct.js
│   │   ├── PhysicalProduct.js
│   │   ├── Sale.js
│   │   └── MarketCategory.js
│   ├── utils/
│   │   ├── dataProcessor.js
│   │   ├── analytics.js
│   │   └── cache.js
│   ├── services/
│   │   ├── MarketplaceService.js
│   │   └── ReportingService.js
│   ├── database/
│   │   ├── db.js
│   │   └── seed.js
│   ├── locales/
│   │   ├── en.json
│   │   ├── fr.json
│   │   └── rw.json
│   └── index.js
├── docs/
│   ├── CONCEPTS.md
│   └── API.md
├── .eslintrc.js
├── package.json
├── README.md
└── REFLECTION.md
```

---

## Canvas Instructions for Students

### Getting Started

1. **Form your pair** - coordinate with your partner
2. **Accept the GitHub Classroom assignment** via the link in Canvas
3. **Clone your repository** to both machines
4. **Install dependencies:** `npm install`
5. **Read the concept guides** in `docs/CONCEPTS.md`
6. **Run tests:** `npm test` (initially, all tests will fail)
7. **Work through challenges 0-7** sequentially
8. **Switch driver/navigator roles** regularly

### Time Allocation Guide
- Challenge 0: 45 minutes
- Challenge 1: 1 hour
- Challenge 2: 1.5 hours
- Challenge 3: 1.5 hours
- Challenge 4: 1 hour
- Challenge 5: 1 hour
- Challenge 6: 1 hour
- Challenge 7 (Final): 2-3 hours

### Submission Requirements

- Complete all 7 challenges + final challenge
- All tests must pass (`npm test`)
- Code must pass linting (`npm run lint`)
- Both partners push code to GitHub
- Complete reflection document together
- Submit repository URL and reflection in Canvas

---

## Challenge 0: Creating the Vendor Class

### Concept Review: ES6 Classes

**What are Classes?**
Classes in JavaScript are templates for creating objects. They encapsulate data (properties) and behavior (methods) into a single unit. While JavaScript uses prototypal inheritance under the hood, ES6 classes provide a cleaner, more familiar syntax for developers coming from other object-oriented languages.

**Why Use Classes?**
- **Organization:** Group related data and functions together
- **Reusability:** Create multiple instances from one template
- **Maintainability:** Clear structure makes code easier to understand
- **Encapsulation:** Bundle data with methods that operate on that data

**Basic Syntax:**
```javascript
class ClassName {
  constructor(param1, param2) {
    this.property1 = param1;
    this.property2 = param2;
  }

  methodName() {
    // method body
  }
}

// Creating an instance
const instance = new ClassName(value1, value2);
```

**Key Concepts:**
- **Constructor:** Special method called when creating a new instance
- **this keyword:** Refers to the current instance
- **Instance methods:** Functions that operate on instance data
- **new keyword:** Creates a new instance of the class

### 📖 Additional Resources

**Essential Reading:**
- [MDN: Classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes) - Comprehensive guide
- [JavaScript.info: Classes](https://javascript.info/class) - Interactive tutorial
- [ES6 Classes in Depth](https://exploringjs.com/es6/ch_classes.html) - Deep dive

**Video Tutorials:**
- [JavaScript ES6 Classes - Traversy Media](https://www.youtube.com/watch?v=2ZphE5HcQPQ) - 30 mins
- [Object Oriented JavaScript - The Net Ninja](https://www.youtube.com/playlist?list=PL4cUxeGkcC9i5yvDkJgt60vNVWffpblB7) - Playlist

**Practice:**
- [JavaScript Classes - freeCodeCamp](https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/es6/use-class-syntax-to-define-a-constructor-function)

---

### Challenge 0 Tasks

**File:** `src/models/Vendor.js`

**Objective:** Create a `Vendor` class to represent marketplace vendors.

**Requirements:**

**Part A: Basic Class Structure (15 mins)**
- Constructor should accept: `name`, `stallNumber`, `category`, `location`
- Initialize properties: `revenue` (default: 0), `registrationDate` (current date), `id` (UUID)
- Validate that name and stallNumber are provided (throw error if missing)

**Part B: Instance Methods (20 mins)**
- `getInfo()` - returns formatted vendor information string
- `addRevenue(amount)` - increases vendor revenue, validates amount is positive
- `getRevenueInCurrency(currency, exchangeRate)` - converts revenue to different currencies (RWF, KES, NGN, USD)
- `getDaysActive()` - calculates days since registration

**Part C: Computed Properties (10 mins)**
- `get fullLocation()` - returns formatted string: "Stall {stallNumber} at {location}"
- `get status()` - returns "Active" if revenue > 0, otherwise "Inactive"

**Example Usage:**
```javascript
const vendor = new Vendor('Mama Aisha', 'A-12', 'Textiles', 'Kimironko Market');
vendor.addRevenue(50000);

console.log(vendor.getInfo());
// Output: "Mama Aisha - Stall A-12 (Textiles) at Kimironko Market"

console.log(vendor.fullLocation);
// Output: "Stall A-12 at Kimironko Market"

console.log(vendor.getRevenueInCurrency('USD', 0.00077));
// Output: 38.5

console.log(vendor.status);
// Output: "Active"
```

**Testing:**
```bash
npm test -- 0-vendor.test.js
```

**Pair Programming Checkpoint:**
- Discuss: Why use getters vs regular methods?
- Review: Are your validation checks sufficient?
- Switch roles before moving to Challenge 1

---

## Challenge 1: Product Base Class

### Concept Review: Class Properties and Methods

**Instance Properties:**
Properties that belong to each individual instance of a class. Each object created from the class has its own copy of these properties.

```javascript
class Example {
  constructor(value) {
    this.instanceProperty = value; // Unique to each instance
  }
}
```

**Method Types:**
- **Instance methods:** Called on instances, have access to `this`
- **Getters/Setters:** Special methods that act like properties
- **Private fields:** Use `#` prefix (ES2022) for truly private data

**UUID Generation:**
Universally Unique Identifiers ensure each product has a unique ID. We'll use the `uuid` package:

```javascript
import { v4 as uuidv4 } from 'uuid';
const id = uuidv4(); // Generates: "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
```

**Object Destructuring:**
Extract properties from objects into variables:

```javascript
const person = { name: 'John', age: 30, city: 'Kigali' };

// Old way
const name = person.name;
const age = person.age;

// ES6 destructuring
const { name, age } = person;

// With renaming
const { name: fullName, age: years } = person;

// With defaults
const { name, country = 'Rwanda' } = person;
```

### 📖 Additional Resources

**Essential Reading:**
- [MDN: Destructuring Assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment)
- [MDN: Getters and Setters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/get)
- [JavaScript.info: Property Getters and Setters](https://javascript.info/property-accessors)

**Video Tutorials:**
- [Destructuring in JavaScript - Web Dev Simplified](https://www.youtube.com/watch?v=NIq3qLaHCIs) - 10 mins
- [Getters and Setters in JavaScript](https://www.youtube.com/watch?v=bl98dm7vJt0) - 12 mins

---

### Challenge 1 Tasks

**File:** `src/models/Product.js`

**Objective:** Create a base `Product` class for marketplace items.

**Requirements:**

**Part A: Constructor and Properties (20 mins)**
- Constructor accepts: `name`, `price`, `vendor`, `stockQuantity`
- Auto-generate: `id` (UUID), `createdAt` (timestamp)
- Validate: price must be positive, stockQuantity must be non-negative
- Store vendor reference (the vendor object)

**Part B: Stock Management Methods (20 mins)**
- `updateStock(quantity)` - increases/decreases stock, prevents negative stock
- `isInStock()` - returns boolean (true if stockQuantity > 0)
- `isLowStock(threshold = 5)` - returns true if stock below threshold
- `restock(quantity)` - convenience method to add stock

**Part C: Price Calculations (15 mins)**
- `getPriceWithTax(taxRate)` - calculates price including tax (default 18% for Rwanda)
- `getDiscountedPrice(percentage)` - calculates discounted price
- `get formattedPrice()` - returns price formatted as "RWF 15,000"

**Part D: Data Export (5 mins)**
- `getDetails()` - returns object with all product info using destructuring
- `toJSON()` - returns JSON-friendly representation (exclude vendor object, include vendor name only)

**Example Usage:**
```javascript
const vendor = new Vendor('Mama Rose', 'B-15', 'Handicrafts', 'Nyabugogo');
const product = new Product('Kitenge Fabric', 15000, vendor, 50);

console.log(product.isInStock()); // true
console.log(product.isLowStock(10)); // false

product.updateStock(-45);
console.log(product.isLowStock(10)); // true

console.log(product.getPriceWithTax()); // 17700
console.log(product.formattedPrice); // "RWF 15,000"

const { name, price, stockQuantity } = product.getDetails();
console.log(name); // "Kitenge Fabric"
```

**Pair Programming Checkpoint:**
- Discuss: When should you throw errors vs return false?
- Review: How does destructuring simplify your code?
- Switch roles before moving to Challenge 2

---

## Challenge 2: Inheritance - Specialized Product Types

### Concept Review: Class Inheritance

**What is Inheritance?**
Inheritance allows you to create a new class based on an existing class. The new class (child/subclass) inherits properties and methods from the existing class (parent/superclass) and can add its own unique features.

**Why Use Inheritance?**
- **Code Reuse:** Don't repeat common functionality
- **Organization:** Create hierarchies that reflect real-world relationships
- **Polymorphism:** Different classes can be used interchangeably through a common interface
- **Maintainability:** Update common behavior in one place

**Key Syntax:**
```javascript
class Parent {
  constructor(param) {
    this.property = param;
  }
  
  parentMethod() {
    return 'From parent';
  }
}

class Child extends Parent {
  constructor(param, childParam) {
    super(param); // Call parent constructor
    this.childProperty = childParam;
  }
  
  // Override parent method
  parentMethod() {
    return 'From child';
  }
  
  // New method
  childMethod() {
    return 'Only in child';
  }
}
```

**Important Concepts:**
- **extends keyword:** Creates inheritance relationship
- **super():** Calls parent class constructor (must be first in child constructor)
- **super.method():** Calls parent class methods
- **Method overriding:** Child class can replace parent methods
- **Method extension:** Child can call parent method and add to it

**Polymorphism Example:**
```javascript
function processProduct(product) {
  console.log(product.getDetails()); // Works for any Product subclass
}

processProduct(new PhysicalProduct(...)); // Works
processProduct(new DigitalProduct(...));  // Works
```

### 📖 Additional Resources

**Essential Reading:**
- [MDN: Inheritance and the Prototype Chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)
- [MDN: extends](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/extends)
- [JavaScript.info: Class Inheritance](https://javascript.info/class-inheritance)
- [Understanding Prototypes and Inheritance](https://www.digitalocean.com/community/tutorials/understanding-prototypes-and-inheritance-in-javascript)

**Video Tutorials:**
- [JavaScript Inheritance - Programming with Mosh](https://www.youtube.com/watch?v=MfxBfRD0FVU) - 15 mins
- [ES6 Class Inheritance - Academind](https://www.youtube.com/watch?v=RBLIm5LMrmc) - 18 mins

**Advanced Reading:**
- [Composition vs Inheritance](https://www.thoughtworks.com/insights/blog/composition-vs-inheritance-how-choose)

---

### Challenge 2 Tasks

**Files:** `src/models/PhysicalProduct.js`, `src/models/DigitalProduct.js`

**Objective:** Implement inheritance for different product types.

**Part A: PhysicalProduct Class (45 mins)**

**Requirements:**
- Extends `Product` class
- Additional constructor parameters: `weight` (kg), `dimensions` (object: {length, width, height} in cm)
- Additional properties: `shippingZone` (default: 'local')
- Override `getDetails()` to include physical attributes
- New methods:
  - `calculateShippingCost(distance)` - based on weight and distance
    - Local (< 10km): RWF 1000 base + (weight * 500)
    - Regional (< 100km): RWF 2000 base + (weight * 800)
    - National (> 100km): RWF 5000 base + (weight * 1200)
  - `getVolume()` - calculates volume from dimensions
  - `get shippingCategory()` - returns "Light", "Medium", or "Heavy" based on weight
    - Light: < 2kg
    - Medium: 2-10kg
    - Heavy: > 10kg

**Example Usage:**
```javascript
const fabric = new PhysicalProduct(
  'Kitenge Fabric',
  15000,
  vendor,
  50,
  2, // weight in kg
  { length: 100, width: 150, height: 1 } // dimensions in cm
);

console.log(fabric.calculateShippingCost(5));  // RWF 2000 (local)
console.log(fabric.calculateShippingCost(50)); // RWF 3600 (regional)
console.log(fabric.getVolume());               // 15000 cm³
console.log(fabric.shippingCategory);          // "Medium"

const details = fabric.getDetails();
console.log(details.weight);     // 2
console.log(details.dimensions); // { length: 100, width: 150, height: 1 }
```

**Part B: DigitalProduct Class (45 mins)**

**Requirements:**
- Extends `Product` class
- Additional constructor parameters: `downloadUrl`, `fileSize` (MB), `format` (e.g., 'PDF', 'MP4', 'ZIP')
- Additional properties: `downloadCount` (default: 0), `licenseType` (default: 'single-use')
- Override `isInStock()` to always return `true` (digital products don't run out)
- Override `updateStock()` to do nothing (but don't throw error)
- Override `getDetails()` to include digital attributes
- New methods:
  - `getDownloadLink(customerId)` - returns object with time-limited download link
  - `recordDownload()` - increments download count
  - `get downloadSize()` - returns formatted file size (e.g., "2.5 MB", "1.2 GB")
  - `estimateDownloadTime(speedMbps)` - calculates download time in seconds
  - `get isLargeFile()` - returns true if file > 100MB

**Example Usage:**
```javascript
const ebook = new DigitalProduct(
  'Market Guide PDF',
  5000,
  vendor,
  999,
  'https://storage.example.com/guide.pdf',
  2.5, // 2.5 MB
  'PDF'
);

console.log(ebook.isInStock()); // Always true
ebook.updateStock(-100);         // Does nothing, no error
console.log(ebook.isInStock()); // Still true

const link = ebook.getDownloadLink('customer-123');
console.log(link);
// { url: '...', expiresAt: '2025-11-12T10:30:00Z', customerId: 'customer-123' }

console.log(ebook.downloadSize); // "2.5 MB"
console.log(ebook.estimateDownloadTime(10)); // ~2 seconds (at 10 Mbps)
console.log(ebook.isLargeFile); // false

ebook.recordDownload();
console.log(ebook.downloadCount); // 1
```

**Pair Programming Checkpoint:**
- Discuss: How does inheritance reduce code duplication?
- Review: When did you need to call `super()`?
- Discuss: Why does `DigitalProduct` override `isInStock()`?
- Switch roles before moving to Challenge 3

---

## Challenge 3: Data Manipulation with Array Methods

### Concept Review: ES6 Array and Object Methods

**Array Methods Overview:**

**1. map() - Transform Each Element**
Creates a new array by applying a function to each element.

```javascript
const prices = [1000, 2000, 3000];
const withTax = prices.map(price => price * 1.18);
// [1180, 2360, 3540]

const products = [
  { name: 'Item 1', price: 1000 },
  { name: 'Item 2', price: 2000 }
];
const names = products.map(p => p.name);
// ['Item 1', 'Item 2']
```

**When to use map:**
- Transform data structure
- Extract specific properties
- Apply calculations to each item

**2. filter() - Select Elements**
Creates a new array with elements that pass a test.

```javascript
const numbers = [1, 2, 3, 4, 5];
const evens = numbers.filter(n => n % 2 === 0);
// [2, 4]

const products = [
  { name: 'A', stock: 5 },
  { name: 'B', stock: 0 },
  { name: 'C', stock: 10 }
];
const inStock = products.filter(p => p.stock > 0);
// [{ name: 'A', stock: 5 }, { name: 'C', stock: 10 }]
```

**When to use filter:**
- Find items matching criteria
- Remove unwanted elements
- Subset data

**3. reduce() - Combine Elements**
Reduces array to a single value by applying a function.

```javascript
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((total, num) => total + num, 0);
// 15

const products = [
  { name: 'A', price: 1000, quantity: 2 },
  { name: 'B', price: 2000, quantity: 1 }
];
const totalValue = products.reduce((sum, p) => sum + (p.price * p.quantity), 0);
// 4000

// Group by category
const grouped = products.reduce((acc, product) => {
  const category = product.category;
  if (!acc[category]) acc[category] = [];
  acc[category].push(product);
  return acc;
}, {});
```

**When to use reduce:**
- Calculate totals/averages
- Group data
- Transform arrays into objects
- Complex aggregations

**4. sort() - Reorder Elements**
Sorts array in place (mutates original).

```javascript
const numbers = [3, 1, 4, 1, 5];
numbers.sort((a, b) => a - b); // Ascending
// [1, 1, 3, 4, 5]

numbers.sort((a, b) => b - a); // Descending
// [5, 4, 3, 1, 1]

const vendors = [
  { name: 'A', revenue: 50000 },
  { name: 'B', revenue: 30000 }
];
vendors.sort((a, b) => b.revenue - a.revenue); // Highest first
```

**5. Other Useful Methods:**
```javascript
// find - get first matching element
const found = products.find(p => p.id === '123');

// some - test if any element matches
const hasExpensive = products.some(p => p.price > 10000);

// every - test if all elements match
const allInStock = products.every(p => p.stock > 0);

// slice - get portion of array (doesn't mutate)
const top3 = vendors.slice(0, 3);
```

**Method Chaining:**
Combine multiple methods for powerful data processing:

```javascript
const result = products
  .filter(p => p.stock > 0)           // Only in-stock items
  .map(p => ({ ...p, total: p.price * p.stock }))  // Add total value
  .sort((a, b) => b.total - a.total) // Sort by value
  .slice(0, 5);                       // Get top 5
```

### 📖 Additional Resources

**Essential Reading:**
- [MDN: Array Methods](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [JavaScript.info: Array Methods](https://javascript.info/array-methods)
- [Map, Filter, Reduce Explained](https://www.freecodecamp.org/news/javascript-map-reduce-and-filter-explained-with-examples/)

**Video Tutorials:**
- [Map, Filter, Reduce - Fun Fun Function](https://www.youtube.com/watch?v=BMUiFMZr7vk) - 11 mins
- [JavaScript Array Methods - Traversy Media](https://www.youtube.com/watch?v=R8rmfD9Y5-c) - 26 mins
- [Functional Programming in JavaScript](https://www.youtube.com/watch?v=e-5obm1G_FY) - 30 mins

**Practice:**
- [Array Methods Practice - freeCodeCamp](https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/#functional-programming)

---

### Challenge 3 Tasks

**File:** `src/utils/dataProcessor.js`

**Objective:** Create utility functions using ES6 array and object manipulation.

**Part A: Filtering Functions (20 mins)**

```javascript
// 1. Get all products from a specific category
export function getProductsByCategory(products, category) {
  // Use filter
  // Return array of products matching category
}

// 2. Find low-stock products
export function getLowStockProducts(products, threshold = 10) {
  // Use filter
  // Return products where stockQuantity < threshold
  // Only include products that CAN be out of stock (physical products)
}

// 3. Get products by vendor
export function getProductsByVendor(products, vendorName) {
  // Use filter
  // Return products from specific vendor
}

// 4. Get products in price range
export function getProductsInPriceRange(products, minPrice, maxPrice) {
  // Use filter
  // Return products where price is between min and max (inclusive)
}
```

**Part B: Transformation Functions (25 mins)**

```javascript
// 5. Get product summaries (name, price, vendor name only)
export function getProductSummaries(products) {
  // Use map and destructuring
  // Return array of objects: { name, price, vendorName }
}

// 6. Add tax to all products
export function addTaxToProducts(products, taxRate = 0.18) {
  // Use map
  // Return new array with priceWithTax property added
  // Don't modify original products
}

// 7. Format products for display
export function formatProductsForDisplay(products) {
  // Use map
  // Return array with formatted strings:
  // "Product Name - RWF XX,XXX (XX in stock)"
}

// 8. Extract unique categories
export function getUniqueCategories(products) {
  // Use map and Set
  // Return array of unique vendor categories
}
```

**Part C: Aggregation Functions (30 mins)**

```javascript
// 9. Calculate total inventory value
export function calculateInventoryValue(products) {
  // Use reduce
  // Return sum of (price * stockQuantity) for all products
}

// 10. Calculate average product price by category
export function getAveragePriceByCategory(products) {
  // Use reduce to group, then calculate averages
  // Return object: { category: averagePrice, ... }
}

// 11. Group products by vendor
export function groupProductsByVendor(products) {
  // Use reduce
  // Return object: { vendorName: [products...], ... }
}

// 12. Get revenue by vendor
export function getRevenueByVendor(vendors) {
  // Use reduce
  // Return object: { vendorName: revenue, ... }
}

// 13. Calculate statistics
export function calculateProductStatistics(products) {
  // Use reduce
  // Return object with:
  // - totalProducts: count
  // - totalValue: sum of all inventory values
  // - averagePrice: mean price
  // - lowestPrice: minimum
  // - highestPrice: maximum
}
```

**Part D: Sorting and Complex Operations (25 mins)**

```javascript
// 14. Get top N vendors by revenue
export function getTopVendors(vendors, n = 5) {
  // Use sort and slice
  // Return array of top vendors by revenue (highest first)
  // Don't mutate original array
}

// 15. Get most popular products by stock movement
export function getMostPopularProducts(products, n = 10) {
  // Assumes products have an 'initialStock' property
  // Use sort and slice
  // Calculate popularity as: initialStock - currentStock
  // Return top N products
}

// 16. Get vendor performance rankings
export function getVendorPerformanceRankings(vendors) {
  // Use sort and map
  // Return array of objects: { rank, name, revenue, category }
  // Sorted by revenue (highest first)
}

// 17. Get filtered, sorted, and formatted products
export function getProductCatalog(products, options = {}) {
  // Chain multiple methods
  // Options: { category, minPrice, maxPrice, sortBy, limit }
  // Return filtered, sorted, limited array
  // Default sort: by price ascending
}
```

**Example Usage:**
```javascript
// Import sample data
import { vendors, products } from '../database/seed.js';

// Filtering
const textiles = getProductsByCategory(products, 'Textiles');
const lowStock = getLowStockProducts(products, 5);
const affordable = getProductsInPriceRange(products, 0, 20000);

// Transformation
const summaries = getProductSummaries(products);
// [{ name: 'Kitenge', price: 15000, vendorName: 'Mama Rose' }, ...]

const displayed = formatProductsForDisplay(products);
// ["Kitenge - RWF 15,000 (50 in stock)", ...]

// Aggregation
const totalValue = calculateInventoryValue(products);
console.log(`Total inventory: RWF ${totalValue.toLocaleString()}`);

const avgByCategory = getAveragePriceByCategory(products);
console.log(avgByCategory);
// { Textiles: 15000, Electronics: 45000, Handicrafts: 12000 }

const grouped = groupProductsByVendor(products);
console.log(grouped['Mama Rose']); // Array of her products

const stats = calculateProductStatistics(products);
console.log(stats);
// { totalProducts: 150, totalValue: 5000000, averagePrice: 18500, ... }

// Sorting
const topVendors = getTopVendors(vendors, 5);
console.log(topVendors[0]); // Highest revenue vendor

// Complex
const catalog = getProductCatalog(products, {
  category: 'Textiles',
  minPrice: 10000,
  maxPrice: 50000,
  sortBy: 'price',
  limit: 10
});
```

**Pair Programming Checkpoint:**
- Discuss: When would you use reduce instead of a for loop?
- Review: How does method chaining improve readability?
- Discuss: Why create new arrays instead of mutating originals?
- Switch roles before moving to Challenge 4

---

## Challenge 4: Sales Tracking with Classes

### Concept Review: Static Methods and Date Handling

**Static Methods:**
Static methods belong to the class itself, not to instances. They're useful for utility functions related to the class.

```javascript
class MathHelper {
  static add(a, b) {
    return a + b;
  }
}

// Called on the class
MathHelper.add(2, 3); // 5

// NOT on instances
const helper = new MathHelper();
helper.add(2, 3); // ERROR
```

**When to use static methods:**
- Factory functions (create instances)
- Utility functions that operate on multiple instances
- Validation or transformation functions
- Aggregate operations (calculate totals, averages, etc.)

**Date Handling in JavaScript:**
```javascript
// Create dates
const now = new Date();
const specific = new Date('2025-01-15');
const fromTimestamp = new Date(1699876543000);

// Get components
now.getFullYear();  // 2025
now.getMonth();     // 0-11 (0 = January)
now.getDate();      // 1-31
now.getDay();       // 0-6 (0 = Sunday)
now.getHours();     // 0-23

// Comparison
const date1 = new Date('2025-01-15');
const date2 = new Date('2025-01-20');
date1 < date2; // true

// Difference in milliseconds
const diff = date2 - date1;
const days = diff / (1000 * 60 * 60 * 24); // Convert to days

// Formatting (basic)
now.toISOString(); // "2025-11-11T08:30:00.000Z"
now.toLocaleDateString(); // "11/11/2025"
now.toLocaleString('en-GB'); // "11/11/2025, 08:30:00"
```

**Working with Time Periods:**
```javascript
// Start of today
const startOfDay = new Date();
startOfDay.setHours(0, 0, 0, 0);

// End of today
const endOfDay = new Date();
endOfDay.setHours(23, 59, 59, 999);

// Check if date is today
function isToday(date) {
  const today = new Date();
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear();
}

// Get start of month
function getStartOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}
```

### 📖 Additional Resources

**Essential Reading:**
- [MDN: Static Methods](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/static)
- [MDN: Date](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
- [JavaScript.info: Date and Time](https://javascript.info/date)
- [Working with Dates - JavaScript.info](https://javascript.info/date)

**Video Tutorials:**
- [JavaScript Static Methods](https://www.youtube.com/watch?v=xjISNOe6mHg) - 8 mins
- [JavaScript Dates - Programming with Mosh](https://www.youtube.com/watch?v=-eRsWqwcPuk) - 14 mins

---

### Challenge 4 Tasks

**File:** `src/models/Sale.js`

**Objective:** Create a `Sale` class to track marketplace transactions.

**Part A: Basic Sale Class (25 mins)**

**Requirements:**
- Constructor accepts: `product`, `quantity`, `customer` (optional object with name, phone, email)
- Auto-generate: `id` (UUID), `timestamp` (current date/time)
- Calculate: `totalAmount` (product.price * quantity * (1 + taxRate)), `taxAmount`
- Validate: quantity must be positive, product must have sufficient stock
- Update product stock when sale is created
- Properties: `status` (default: 'completed'), `paymentMethod` (default: 'cash')

**Instance Methods:**
- `getReceipt()` - returns formatted receipt object with all sale details
- `refund()` - marks sale as refunded, restores product stock
- `get isRefunded()` - returns boolean
- `getDaysAgo()` - returns number of days since sale

**Part B: Static Analysis Methods (35 mins)**

Implement these static methods for analyzing sales data:

```javascript
// 1. Filter sales by time period
static getTodaysSales(sales) {
  // Return sales from today
}

static getSalesInRange(sales, startDate, endDate) {
  // Return sales between dates (inclusive)
}

static getThisMonthSales(sales) {
  // Return sales from current month
}

// 2. Revenue calculations
static calculateTotalRevenue(sales) {
  // Use reduce to sum all sale amounts
  // Exclude refunded sales
}

static getRevenueByPeriod(sales) {
  // Return object with revenue grouped by date
  // Format: { '2025-11-11': 150000, '2025-11-12': 200000, ... }
}

static getRevenueByVendor(sales) {
  // Return object with revenue per vendor
  // Use reduce
}

// 3. Product analytics
static getMostPopularProducts(sales, limit = 10) {
  // Calculate total quantity sold per product
  // Return array of products sorted by quantity sold
  // Format: [{ product, totalQuantity, revenue }, ...]
}

static getLeastPopularProducts(sales, limit = 10) {
  // Opposite of above
}

// 4. Customer analytics
static getTopCustomers(sales, limit = 10) {
  // Find customers with highest total purchase amounts
  // Filter out sales without customer info
  // Return: [{ customer, totalSpent, purchaseCount }, ...]
}

static getAverageOrderValue(sales) {
  // Calculate mean sale amount
}

// 5. Time-based analytics
static getSalesByHour(sales) {
  // Group sales by hour of day (0-23)
  // Return: { 0: count, 1: count, ..., 23: count }
}

static getSalesByDayOfWeek(sales) {
  // Group sales by day (0=Sunday, 6=Saturday)
  // Return: { 0: count, ..., 6: count }
}

// 6. Performance metrics
static getConversionMetrics(sales, totalVisitors) {
  // Calculate conversion rate
  // Average items per transaction
  // Return metrics object
}

static getSalesGrowth(currentPeriodSales, previousPeriodSales) {
  // Calculate growth percentage
  // Return { current, previous, growth, growthPercentage }
}
```

**Example Usage:**
```javascript
const sale = new Sale(product, 3, {
  name: 'Jean Paul',
  phone: '0788123456',
  email: 'jean@example.com'
});

console.log(sale.totalAmount); // 53100 (15000 * 3 * 1.18)
console.log(sale.getReceipt());
/*
{
  id: '...',
  timestamp: '2025-11-11T10:30:00.000Z',
  product: 'Kitenge Fabric',
  vendor: 'Mama Rose',
  quantity: 3,
  unitPrice: 15000,
  subtotal: 45000,
  tax: 8100,
  total: 53100,
  customer: { name: 'Jean Paul', phone: '0788123456' },
  status: 'completed'
}
*/

sale.refund();
console.log(sale.isRefunded); // true
console.log(product.stockQuantity); // Stock restored

// Static methods
const allSales = [...]; // Array of Sale instances

const todaySales = Sale.getTodaysSales(allSales);
const revenue = Sale.calculateTotalRevenue(todaySales);
console.log(`Today's revenue: RWF ${revenue.toLocaleString()}`);

const popular = Sale.getMostPopularProducts(allSales, 5);
console.log('Top 5 Products:', popular);

const topCustomers = Sale.getTopCustomers(allSales, 10);
const avgOrder = Sale.getAverageOrderValue(allSales);

const revenueByVendor = Sale.getRevenueByVendor(allSales);
console.log(revenueByVendor);
// { 'Mama Rose': 250000, 'Jean Claude': 180000, ... }

const hourly = Sale.getSalesByHour(allSales);
// Shows which hours are busiest
```

**Pair Programming Checkpoint:**
- Discuss: Why are the analytics methods static?
- Review: How do you handle dates across time zones?
- Discuss: What edge cases did you encounter?
- Switch roles before moving to Challenge 5

---

## Challenge 5: Advanced Analytics

### Concept Review: Complex Data Processing

**Combining Multiple Operations:**
Real-world analytics often require chaining multiple array methods and combining different data sources.

**Pattern: Filter → Map → Reduce**
```javascript
const result = data
  .filter(item => /* condition */)
  .map(item => /* transform */)
  .reduce((acc, item) => /* aggregate */, initial);
```

**Grouping and Aggregating:**
```javascript
// Group by key, then calculate aggregates
function analyzeByCategory(items) {
  // Step 1: Group
  const grouped = items.reduce((acc, item) => {
    const key = item.category;
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});
  
  // Step 2: Aggregate each group
  return Object.entries(grouped).map(([category, items]) => ({
    category,
    count: items.length,
    total: items.reduce((sum, item) => sum + item.value, 0),
    average: items.reduce((sum, item) => sum + item.value, 0) / items.length
  }));
}
```

**Time Series Analysis:**
```javascript
// Compare periods
function comparePeriods(data, periodDays) {
  const now = new Date();
  const periodAgo = new Date(now - periodDays * 24 * 60 * 60 * 1000);
  const twoPeriodAgo = new Date(now - 2 * periodDays * 24 * 60 * 60 * 1000);
  
  const current = data.filter(item => item.date >= periodAgo);
  const previous = data.filter(item => 
    item.date >= twoPeriodAgo && item.date < periodAgo
  );
  
  return {
    current: calculate(current),
    previous: calculate(previous),
    change: calculate(current) - calculate(previous)
  };
}
```

### 📖 Additional Resources

**Essential Reading:**
- [Advanced Array Methods](https://eloquentjavascript.net/05_higher_order.html)
- [Functional JavaScript](https://mostly-adequate.gitbook.io/mostly-adequate-guide/)

---

### Challenge 5 Tasks

**File:** `src/utils/analytics.js`

**Objective:** Create advanced analytics functions for marketplace insights.

**Part A: Vendor Analytics (30 mins)**

```javascript
// 1. Comprehensive vendor performance
export function analyzeVendorPerformance(vendors, sales, products) {
  // For each vendor, calculate:
  // - Total revenue
  // - Number of products
  // - Total sales count
  // - Average sale value
  // - Best-selling product
  // - Revenue trend (last 7 days vs previous 7 days)
  // Return array sorted by revenue
}

// 2. Vendor comparison
export function compareVendors(vendor1Id, vendor2Id, sales, products) {
  // Compare two vendors across multiple metrics
  // Return detailed comparison object
}

// 3. Identify rising stars
export function findRisingStarVendors(vendors, sales, daysToCompare = 30) {
  // Find vendors with significant revenue growth
  // Compare recent period vs previous period
  // Return vendors with >50% growth
}
```

**Part B: Product Analytics (30 mins)**

```javascript
// 4. Product performance matrix
export function analyzeProductPerformance(products, sales) {
  // Categorize products into quadrants:
  // - Stars: High sales, High margin
  // - Cash Cows: High sales, Low margin
  // - Question Marks: Low sales, High margin
  // - Dogs: Low sales, Low margin
  // Return object with arrays for each quadrant
}

// 5. Inventory optimization
export function getInventoryRecommendations(products, sales, daysToAnalyze = 30) {
  // Calculate turnover rate for each product
  // Identify: overstocked, understocked, optimal
  // Suggest reorder quantities
  // Return recommendations array
}

// 6. Price elasticity analysis
export function analyzePricePerformance(products, sales) {
  // For products in similar categories
  // Analyze relationship between price and sales volume
  // Identify pricing opportunities
}
```

**Part C: Market Insights (30 mins)**

```javascript
// 7. Category trends
export function analyzeCategoryTrends(products, sales, months = 3) {
  // Track category performance over time
  // Identify growing/declining categories
  // Return trend data
}

// 8. Customer behavior analysis
export function analyzeCustomerBehavior(sales) {
  // Calculate:
  // - Average time between purchases (for repeat customers)
  // - Basket size distribution
  // - Peak shopping times
  // - Customer lifetime value
  // Return insights object
}

// 9. Market basket analysis
export function findProductAssociations(sales) {
  // Find products frequently bought together
  // Calculate association strength
  // Return array of product pairs with confidence scores
}

// 10. Seasonal patterns
export function identifySeasonalPatterns(sales, products) {
  // Group sales by month
  // Identify seasonal products
  // Calculate seasonality index for each product
}
```

**Example Usage:**
```javascript
const vendorPerformance = analyzeVendorPerformance(vendors, sales, products);
console.log(vendorPerformance[0]);
/*
{
  vendor: 'Mama Rose',
  revenue: 2500000,
  productCount: 45,
  salesCount: 320,
  averageSale: 7812,
  bestProduct: 'Kitenge Fabric',
  revenueGrowth: 23.5, // percentage
  trend: 'up'
}
*/

const risingStars = findRisingStarVendors(vendors, sales, 30);
console.log(`${risingStars.length} vendors showing strong growth`);

const productMatrix = analyzeProductPerformance(products, sales);
console.log('Star Products:', productMatrix.stars.length);

const recommendations = getInventoryRecommendations(products, sales);
recommendations.forEach(rec => {
  if (rec.status === 'understocked') {
    console.log(`Reorder ${rec.product}: suggested quantity ${rec.reorderQty}`);
  }
});

const behavior = analyzeCustomerBehavior(sales);
console.log('Average purchase frequency:', behavior.avgDaysBetweenPurchases);
console.log('Peak hours:', behavior.peakHours); // [10, 11, 14, 15]
```

**Pair Programming Checkpoint:**
- Discuss: What insights are most valuable for vendors?
- Review: How do you handle edge cases (no data)?
- Switch roles before moving to Challenge 6

---

## Challenge 6: Integration with Redis and Database

### Concept Review: Caching Strategies

**What is Caching?**
Caching stores frequently accessed data in a fast-access location (like Redis) to reduce database queries and improve performance.

**When to Cache:**
- Frequently accessed data (product catalogs, vendor lists)
- Expensive calculations (analytics, reports)
- Data that doesn't change often
- Data that's okay to be slightly stale

**Cache Strategies:**

**1. Cache-Aside (Lazy Loading):**
```javascript
async function getData(key) {
  // Try cache first
  let data = await cache.get(key);
  
  if (!data) {
    // Cache miss - get from database
    data = await database.query(key);
    // Store in cache for next time
    await cache.set(key, data, TTL);
  }
  
  return data;
}
```

**2. Write-Through:**
```javascript
async function saveData(key, data) {
  // Write to database
  await database.save(key, data);
  // Update cache
  await cache.set(key, data, TTL);
}
```

**3. Cache Invalidation:**
```javascript
async function updateData(key, data) {
  // Update database
  await database.update(key, data);
  // Invalidate cache
  await cache.delete(key);
  // Or update cache directly
  await cache.set(key, data, TTL);
}
```

**Redis Basics:**
```javascript
import redis from 'redis';

const client = redis.createClient({
  url: 'redis://localhost:6379'
});

await client.connect();

// String operations
await client.set('key', 'value');
await client.setEx('key', 3600, 'value'); // With TTL
const value = await client.get('key');

// JSON data (store as string)
await client.set('user:123', JSON.stringify(userData));
const userData = JSON.parse(await client.get('user:123'));

// Hash operations
await client.hSet('vendor:123', 'name', 'Mama Rose');
await client.hSet('vendor:123', 'revenue', '50000');
const vendorData = await client.hGetAll('vendor:123');

// Lists
await client.lPush('recent:sales', saleId);
const recentSales = await client.lRange('recent:sales', 0, 9); // Get 10 most recent

// Expiration
await client.expire('key', 3600); // 1 hour
```

### 📖 Additional Resources

**Essential Reading:**
- [Redis Documentation](https://redis.io/docs/)
- [Caching Strategies](https://codeahoy.com/2017/08/11/caching-strategies-and-how-to-choose-the-right-one/)
- [Redis with Node.js](https://redis.io/docs/connect/clients/nodejs/)

**Video Tutorials:**
- [Redis Crash Course](https://www.youtube.com/watch?v=jgpVdJB2sKQ) - 1 hour
- [Caching Strategies Explained](https://www.youtube.com/watch?v=U3RkDLtS7uY) - 15 mins

---

### Challenge 6 Tasks

**Files:** `src/utils/cache.js`, `src/services/MarketplaceService.js`

**Part A: Cache Layer (30 mins)**

**File:** `src/utils/cache.js`

```javascript
import redis from 'redis';

export class MarketplaceCache {
  constructor(redisUrl = 'redis://localhost:6379') {
    // Initialize Redis client
    // Handle connection errors
  }

  async connect() {
    // Connect to Redis
  }

  async disconnect() {
    // Cleanup
  }

  // Vendor caching
  async cacheVendor(vendorId, vendorData, ttl = 3600) {
    // Store vendor data with expiration
  }

  async getCachedVendor(vendorId) {
    // Retrieve vendor from cache
    // Return null if not found
  }

  async invalidateVendor(vendorId) {
    // Remove vendor from cache
  }

  // Product caching
  async cacheProduct(productId, productData, ttl = 3600) {
    // Store product data
  }

  async getCachedProduct(productId) {
    // Retrieve product
  }

  async cacheProductList(key, products, ttl = 1800) {
    // Cache array of products (e.g., popular products)
  }

  async getCachedProductList(key) {
    // Retrieve product list
  }

  // Analytics caching (longer TTL for expensive calculations)
  async cacheAnalytics(key, data, ttl = 7200) {
    // Store analytics results
  }

  async getCachedAnalytics(key) {
    // Retrieve analytics
  }

  // Clear all caches (useful for testing)
  async clearAll() {
    // Flush all cache
  }

  // Get cache statistics
  async getStats() {
    // Return info about cache usage
  }
}
```

**Part B: Marketplace Service (30 mins)**

**File:** `src/services/MarketplaceService.js`

```javascript
import { MarketplaceCache } from '../utils/cache.js';
import { db } from '../database/db.js';

export class MarketplaceService {
  constructor() {
    this.cache = new MarketplaceCache();
    // Initialize database connection
  }

  async initialize() {
    await this.cache.connect();
  }

  // Vendor operations with caching
  async getVendor(vendorId) {
    // Try cache first (cache-aside pattern)
    // If miss, load from database and cache
  }

  async createVendor(vendorData) {
    // Save to database
    // Cache the new vendor
  }

  async updateVendor(vendorId, updates) {
    // Update database
    // Invalidate cache
  }

  // Product operations with caching
  async getProduct(productId) {
    // Implement cache-aside
  }

  async getPopularProducts(limit = 10) {
    // Check cache for popular products
    // If miss, calculate from sales and cache
    // Use shorter TTL (30 mins) since it changes frequently
  }

  async getProductsByCategory(category) {
    // Cache by category
  }

  // Analytics with caching
  async getDashboardStats() {
    // Try cache first
    // If miss, calculate expensive stats:
    // - Total vendors, products, sales
    // - Revenue (today, this month, all time)
    // - Top performers
    // Cache for 1 hour
  }

  async getVendorPerformance(vendorId) {
    // Cache vendor-specific analytics
  }

  // Sales operations
  async recordSale(saleData) {
    // Save sale to database
    // Invalidate affected caches:
    // - Product stock
    // - Popular products
    // - Dashboard stats
    // - Vendor performance
  }

  // Cleanup
  async shutdown() {
    await this.cache.disconnect();
    // Close database connection
  }
}
```

**Example Usage:**
```javascript
const marketplace = new MarketplaceService();
await marketplace.initialize();

// First call - cache miss, loads from DB
const vendor = await marketplace.getVendor('vendor-123');
console.log('First call duration:', /* ~50ms from DB */);

// Second call - cache hit
const vendor2 = await marketplace.getVendor('vendor-123');
console.log('Second call duration:', /* ~2ms from cache */);

// Dashboard stats (expensive calculation)
const stats = await marketplace.getDashboardStats();
// Subsequent calls will be instant for 1 hour

// Record sale - invalidates related caches
await marketplace.recordSale({
  productId: 'product-456',
  quantity: 2,
  customer: { name: 'Alice' }
});

// Cache stats
const cacheStats = await marketplace.cache.getStats();
console.log('Cache hit rate:', cacheStats.hitRate);
```

**Pair Programming Checkpoint:**
- Discuss: When should you invalidate vs update cache?
- Review: What's your cache hit rate?
- Discuss: What are the trade-offs of longer TTLs?
- Switch roles before moving to Final Challenge

---

## Challenge 7: FINAL EXTENDED CHALLENGE
### Complete Marketplace Dashboard with Real-time Features

### Final Challenge Overview

**Duration:** 2-3 hours  
**Objective:** Build a comprehensive marketplace management system that integrates everything you've learned.

This is an open-ended challenge that requires you to combine all concepts:
- ES6 classes with inheritance
- Array/object manipulation
- Static methods and analytics
- Redis caching
- Database integration
- i18n support

---

### Requirements

**File:** `src/services/ReportingService.js` and `src/index.js`

Build a **MarketplaceDashboard** application with the following features:

### Part 1: Dashboard Core (45 mins)

Create a `MarketplaceDashboard` class that provides:

**1. Real-time Statistics**
```javascript
async getDashboardStats() {
  // Return comprehensive dashboard data:
  // - Vendor statistics (total, active, top performers)
  // - Product statistics (total, by category, low stock alerts)
  // - Sales statistics (today, this week, this month)
  // - Revenue metrics (total, average per sale, by period)
  // - Inventory health (total value, turnover rate)
  // Use caching with 15-minute TTL
}
```

**2. Period Comparison Reports**
```javascript
async generatePerformanceReport(startDate, endDate, previousPeriodDays) {
  // Compare current period against previous period:
  // - Revenue growth
  // - Sales volume change
  // - New vs returning customers
  // - Category performance shifts
  // - Vendor ranking changes
  // Include percentage changes and trends
}
```

**3. Vendor Insights Dashboard**
```javascript
async getVendorDashboard(vendorId) {
  // Vendor-specific dashboard with:
  // - Personal sales statistics
  // - Product performance rankings
  // - Revenue trends (7, 30, 90 days)
  // - Comparison against category average
  // - Inventory alerts
  // - Customer feedback summary
  // - Actionable recommendations
}
```

### Part 2: Advanced Analytics (45 mins)

**4. Predictive Analytics**
```javascript
async getPredictiveInsights() {
  // Based on historical data, predict:
  // - Expected sales for next 7 days (by day)
  // - Products likely to stock out (and when)
  // - Revenue forecast for next month
  // - Recommended products to promote
  // Use simple trend analysis (moving averages)
}
```

**5. Market Intelligence**
```javascript
async getMarketIntelligence() {
  // Provide market-level insights:
  // - Category market share
  // - Price positioning (by category)
  // - Competitive analysis (vendor vs vendor)
  // - Demand patterns by time/day
  // - Untapped opportunities
}
```

**6. Alert System**
```javascript
async generateAlerts() {
  // Automated alerts for:
  // - Critical low stock (<5 units)
  // - No sales for 7+ days (stale products)
  // - Unusual price changes
  // - Revenue drops (>20% vs previous period)
  // - High-performing products needing restock
  // Return prioritized alert list
}
```

### Part 3: Reporting & Export (30 mins)

**7. Multi-format Reports**
```javascript
async generateSalesReport(startDate, endDate, format = 'summary') {
  // Formats: 'summary', 'detailed', 'vendor-breakdown'
  // Include charts data (for visualization)
  // Support grouping by: day, week, month
}

async exportToCSV(data, reportType) {
  // Convert any report to CSV format
  // Proper headers and formatting
}

async exportToJSON(reportType, options) {
  // Export comprehensive data as JSON
  // Include metadata
}
```

**8. Internationalization**
```javascript
async getLocalizedDashboard(locale = 'en') {
  // Return dashboard with labels in specified language
  // Supported: 'en', 'fr', 'rw'
  // Format numbers/currency appropriately
  // Translate category names, status labels, etc.
  // Use i18n JSON files from locales/
}
```

### Part 4: Advanced Features (30 mins)

**9. Search and Filtering**
```javascript
async advancedSearch(criteria) {
  // Search across products, vendors, sales
  // Criteria: {
  //   query: string,
  //   filters: { category, priceRange, dateRange },
  //   sortBy: string,
  //   limit: number
  // }
  // Return unified search results
}
```

**10. Data Import/Export**
```javascript
async bulkImportProducts(csvData) {
  // Import products from CSV
  // Validate data
  // Handle errors gracefully
  // Return import summary
}

async bulkUpdateInventory(updates) {
  // Update multiple products at once
  // Format: [{ productId, newStock }, ...]
  // Invalidate relevant caches
}
```

---

### Implementation Guidelines

**Architecture:**
```javascript
// src/index.js - Main application file

import { MarketplaceDashboard } from './services/ReportingService.js';
import { MarketplaceService } from './services/MarketplaceService.js';
import { seedDatabase } from './database/seed.js';

class MarketplaceApp {
  constructor() {
    this.marketplace = new MarketplaceService();
    this.dashboard = new MarketplaceDashboard(this.marketplace);
  }

  async initialize() {
    await this.marketplace.initialize();
    await seedDatabase(); // Load sample data
  }

  async demonstrateFeatures() {
    // Showcase all functionality
    // 1. Display dashboard stats
    // 2. Show vendor performance
    // 3. Generate alerts
    // 4. Export reports
    // 5. Demonstrate caching benefits
  }

  async runPerformanceTest() {
    // Compare performance with/without caching
    // Measure response times
    // Calculate cache hit rates
  }
}

// Main execution
const app = new MarketplaceApp();
await app.initialize();
await app.demonstrateFeatures();
await app.runPerformanceTest();
```

**Class Structure:**
```javascript
export class MarketplaceDashboard {
  constructor(marketplaceService) {
    this.marketplace = marketplaceService;
    this.cache = marketplaceService.cache;
  }

  // Implement all required methods
  // Use helper methods for common operations
  // Handle errors gracefully
  // Log cache hits/misses for monitoring
}
```

---

### Demonstration Script

Create a comprehensive demo that shows:

**1. System Initialization**
```javascript
console.log('Initializing Marketplace Dashboard...\n');
// Load data, connect to Redis, seed database
console.log('System ready\n');
```

**2. Dashboard Overview**
```javascript
console.log(' DASHBOARD OVERVIEW');
console.log('═'.repeat(50));
const stats = await dashboard.getDashboardStats();
console.log(`Total Vendors: ${stats.vendors.total}`);
console.log(`Active Products: ${stats.products.total}`);
console.log(`Today's Revenue: RWF ${stats.revenue.today.toLocaleString()}`);
console.log(`Month's Revenue: RWF ${stats.revenue.month.toLocaleString()}`);
// ... more stats
```

**3. Vendor Spotlight**
```javascript
console.log('\n TOP VENDOR SPOTLIGHT');
console.log('═'.repeat(50));
const topVendor = stats.vendors.topPerformers[0];
const vendorDash = await dashboard.getVendorDashboard(topVendor.id);
// Display comprehensive vendor info
```

**4. Market Intelligence**
```javascript
console.log('\n MARKET INTELLIGENCE');
console.log('═'.repeat(50));
const intelligence = await dashboard.getMarketIntelligence();
// Show insights
```

**5. Alerts**
```javascript
console.log('\n SYSTEM ALERTS');
console.log('═'.repeat(50));
const alerts = await dashboard.generateAlerts();
alerts.forEach((alert, i) => {
  console.log(`${i + 1}. [${alert.priority}] ${alert.message}`);
});
```

**6. Predictions**
```javascript
console.log('\n PREDICTIVE INSIGHTS');
console.log('═'.repeat(50));
const predictions = await dashboard.getPredictiveInsights();
// Show forecasts
```

**7. Performance Metrics**
```javascript
console.log('\n⚡ CACHE PERFORMANCE');
console.log('═'.repeat(50));
const cacheStats = await marketplace.cache.getStats();
console.log(`Hit Rate: ${(cacheStats.hitRate * 100).toFixed(1)}%`);
console.log(`Avg Response Time: ${cacheStats.avgResponseTime}ms`);
```

**8. Localization Demo**
```javascript
console.log('\nINTERNATIONALIZATION');
console.log('═'.repeat(50));
const dashEN = await dashboard.getLocalizedDashboard('en');
const dashFR = await dashboard.getLocalizedDashboard('fr');
const dashRW = await dashboard.getLocalizedDashboard('rw');
// Show same data in different languages
```

---

### Testing Strategy

**File:** `tests/7-final-challenge.test.js`

Your final challenge will be tested on:

1. **Functionality** (40%)
   - All required methods implemented
   - Correct calculations
   - Proper error handling

2. **Integration** (30%)
   - Classes work together
   - Caching implemented correctly
   - Database operations successful

3. **Code Quality** (20%)
   - Clean, readable code
   - Proper use of ES6 features
   - Good naming conventions
   - Adequate comments

4. **Performance** (10%)
   - Efficient algorithms
   - Effective caching
   - Reasonable response times

---

### Creative Extensions (Optional Bonus)

If you complete everything and want more challenges:

1. **Real-time WebSocket Dashboard**
   - Push updates when new sales occur
   - Live revenue counter

2. **Machine Learning Integration**
   - Product recommendation engine
   - Customer segmentation

3. **Notification System**
   - Email/SMS alerts for critical events
   - Configurable alert preferences

4. **Multi-market Support**
   - Handle multiple physical markets
   - Cross-market analytics

5. **Mobile API**
   - REST API for mobile app
   - Authentication layer

6. **Advanced Visualizations**
   - Generate chart data for graphs
   - Export visual reports

---

### Final Submission Checklist

**Code Requirements:**
- [ ] All 7 challenges completed
- [ ] Final challenge fully implemented
- [ ] All tests passing
- [ ] Code follows ESLint rules
- [ ] No console errors
- [ ] Proper error handling throughout

**Documentation:**
- [ ] README.md updated with:
  - Setup instructions
  - How to run the demo
  - API documentation
  - Architecture overview
- [ ] Code comments for complex logic
- [ ] JSDoc comments for public methods

**Reflection (REFLECTION.md):**
Answer these questions together:
1. What was the most challenging part of this activity?
2. How did ES6 classes improve your code organization?
3. Which array method (map/filter/reduce) did you use most and why?
4. What caching strategy worked best for your use case?
5. How did pair programming affect your learning?
6. What would you improve if you had more time?
7. How can you apply these concepts to real-world projects?

**Performance Report:**
- [ ] Cache hit rates documented
- [ ] Response time comparisons (with/without cache)
- [ ] Analytics calculation benchmarks

---

## Class Demonstration

During class, pairs will:
1. **Present** (5 mins): Show your dashboard running
2. **Code Review** (3 mins): Explain one complex function
3. **Q&A** (2 mins): Answer questions from your colleagues

---

## Assessment Rubric

### Automated Testing (50%)
- Challenges 0-6: 35% (5% each)
- Final Challenge: 15%

### Code Quality (25%)
- ES6 Syntax & Features: 8%
- Code Organization: 7%
- Error Handling: 5%
- Documentation: 5%

### Integration & Architecture (15%)
- Components work together: 5%
- Caching implementation: 5%
- Database operations: 5%

### Collaboration & Reflection (10%)
- Git commits from both partners: 3%
- Quality of reflection: 4%
- Code review participation: 3%

**Total: 100%**

---

## Resources Summary

### Essential Reading
- [MDN JavaScript Classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)
- [JavaScript.info ES6+ Features](https://javascript.info/)
- [Eloquent JavaScript - Higher-Order Functions](https://eloquentjavascript.net/05_higher_order.html)

### Practice Platforms
- [freeCodeCamp ES6 Challenges](https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/#es6)
- [JavaScript30 by Wes Bos](https://javascript30.com/)

### African Tech Context
- [GSMA Mobile Economy: Sub-Saharan Africa](https://www.gsma.com/mobileeconomy/sub-saharan-africa/)
- Digital payment systems in East Africa
- E-commerce trends in African markets

---

## Support & Resources

**Canvas Discussion Board:** Post questions, share insights
**Office Hours:** Available for debugging help
**Pair Programming Tips:** Check pinned resources
**Sample Data:** Realistic African marketplace data provided

---

## Learning Outcomes Achieved

By completing this activity, you will have:
Mastered ES6 class syntax and inheritance
Applied functional programming with array methods
Implemented complex data analytics
Integrated caching for performance
Built a complete, production-ready application
Practiced collaborative coding
Solved real-world business problems

**Remember:** This is a learning experience. Don't hesitate to experiment, make mistakes, and ask questions. The goal is understanding, not perfection!

Good luck! # adb-f2
