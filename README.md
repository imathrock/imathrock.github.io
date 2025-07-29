# Personal Portfolio Website - Dark Mode

A modern, responsive personal portfolio website built with HTML, CSS, and JavaScript featuring a beautiful dark mode theme.

## 🌟 Features

- **Dark Mode Design**: Elegant dark theme with blue accent colors
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Smooth Animations**: Scroll-triggered animations and hover effects
- **Interactive Navigation**: Fixed navbar with smooth scrolling
- **Contact Form**: Functional contact form with validation
- **Modern UI**: Clean, professional design with gradient accents
- **Performance Optimized**: Efficient animations and smooth scrolling

## 📁 File Structure

```
Portfolio Website/
├── index.html          # Main HTML file
├── styles.css          # CSS styles and animations
├── script.js           # JavaScript functionality
└── README.md           # This file
```

## 🚀 Getting Started

1. **Open the website**: Simply open `index.html` in your web browser
2. **Customize content**: Edit the HTML file to add your personal information
3. **Modify styling**: Update `styles.css` to change colors, fonts, or layout
4. **Add functionality**: Enhance `script.js` with additional features

## 🎨 Customization Guide

### Personal Information

Edit the following sections in `index.html`:

#### Hero Section
```html
<h1 class="hero-title">
    Hi, I'm <span class="highlight">Your Name</span>
</h1>
<p class="hero-subtitle">Full Stack Developer & Designer</p>
```

#### About Section
```html
<p>
    I'm a passionate developer with a love for creating innovative digital solutions...
</p>
```

#### Contact Information
```html
<div class="contact-item">
    <i class="fas fa-envelope"></i>
    <span>your.email@example.com</span>
</div>
```

### Projects

Add or modify projects in the projects section:

```html
<div class="project-card">
    <div class="project-image">
        <i class="fas fa-laptop-code"></i>
    </div>
    <div class="project-content">
        <h3>Your Project Name</h3>
        <p>Project description goes here...</p>
        <div class="project-tech">
            <span>React</span>
            <span>Node.js</span>
        </div>
        <div class="project-links">
            <a href="#" class="project-link">
                <i class="fas fa-external-link-alt"></i> Live Demo
            </a>
            <a href="#" class="project-link">
                <i class="fab fa-github"></i> Code
            </a>
        </div>
    </div>
</div>
```

### Skills

Update your skills in the skills section:

```html
<div class="skill-item">
    <i class="fab fa-react"></i>
    <span>React</span>
</div>
```

### Colors and Theme

The main color scheme is defined in `styles.css`:

```css
/* Primary colors */
--primary-blue: #60a5fa;
--primary-purple: #a78bfa;
--dark-bg: #0f172a;
--dark-secondary: #1e293b;
--text-primary: #e2e8f0;
--text-secondary: #94a3b8;
```

## 🛠️ Technologies Used

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Flexbox and Grid
- **JavaScript**: Interactive functionality
- **Font Awesome**: Icons
- **Google Fonts**: Inter font family

## 📱 Responsive Design

The website is fully responsive and includes:

- Mobile-first approach
- Hamburger menu for mobile devices
- Flexible grid layouts
- Optimized typography for all screen sizes

## 🎯 Sections Included

1. **Hero Section**: Introduction with call-to-action buttons
2. **About Section**: Personal information and statistics
3. **Projects Section**: Portfolio of work with links
4. **Skills Section**: Technical skills organized by category
5. **Contact Section**: Contact form and social links
6. **Footer**: Copyright information

## 🔧 Advanced Customization

### Adding New Sections

To add a new section, follow this structure:

```html
<section id="new-section" class="new-section">
    <div class="container">
        <h2 class="section-title">Section Title</h2>
        <div class="section-content">
            <!-- Your content here -->
        </div>
    </div>
</section>
```

### Custom Animations

Add custom CSS animations:

```css
@keyframes yourAnimation {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}

.your-element {
    animation: yourAnimation 0.6s ease forwards;
}
```

### Form Integration

To connect the contact form to a backend service:

1. Replace the form action in `index.html`
2. Update the form handling in `script.js`
3. Add your preferred form service (Formspree, Netlify Forms, etc.)

## 🌐 Deployment

### GitHub Pages
1. Push your code to a GitHub repository
2. Go to Settings > Pages
3. Select source branch and save

### Netlify
1. Drag and drop your folder to Netlify
2. Or connect your GitHub repository

### Vercel
1. Import your GitHub repository
2. Deploy automatically

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Feel free to fork this project and customize it for your needs. If you have suggestions or improvements, please open an issue or submit a pull request.

## 📞 Support

If you need help customizing your portfolio or have questions, feel free to reach out!

---

**Happy coding! 🚀** 