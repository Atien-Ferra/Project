/**
 * Index/Landing Page JavaScript
 * ==============================
 * This file handles the landing page animations and interactions:
 * - Hero section animations
 * - Smooth scrolling
 * - Feature cards animations
 * 
 * This page is shown to users who are not logged in.
 */

$(document).ready(function() {
    
    // ============================================
    // HERO SECTION ANIMATIONS
    // ============================================
    
    /**
     * Fade in the hero title on page load
     * Creates a smooth entrance effect
     */
    $(".hero h1").css('opacity', 0).animate({ opacity: 1 }, 800);
    
    /**
     * Fade in the hero subtitle with a slight delay
     */
    $(".hero p").css('opacity', 0).delay(200).animate({ opacity: 1 }, 800);
    
    /**
     * Fade in the hero buttons with more delay
     */
    $(".hero .btn").css('opacity', 0).delay(400).animate({ opacity: 1 }, 600);
    
    // ============================================
    // FEATURE CARDS ANIMATION
    // ============================================
    
    /**
     * Animate feature cards on scroll
     * Cards fade in and slide up when they come into view
     */
    function animateOnScroll() {
        $('.card').each(function() {
            const cardTop = $(this).offset().top;
            const windowBottom = $(window).scrollTop() + $(window).height();
            
            // If card is in viewport
            if (cardTop < windowBottom - 100) {
                $(this).addClass('animate-in');
            }
        });
    }
    
    // Add CSS class for animation
    $('<style>')
        .text(`
            .card {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.5s ease, transform 0.5s ease;
            }
            .card.animate-in {
                opacity: 1;
                transform: translateY(0);
            }
        `)
        .appendTo('head');
    
    // Run on scroll and on page load
    $(window).on('scroll', animateOnScroll);
    animateOnScroll(); // Initial check
    
    // ============================================
    // SMOOTH SCROLLING
    // ============================================
    
    /**
     * Enable smooth scrolling for anchor links
     * When clicking a link that points to an ID on the same page,
     * smoothly scroll to that section instead of jumping
     */
    $('a[href^="#"]').on('click', function(e) {
        const target = $(this).attr('href');
        
        // Only process if target exists and is not just "#"
        if (target && target !== '#' && $(target).length) {
            e.preventDefault();
            
            $('html, body').animate({
                scrollTop: $(target).offset().top - 80 // 80px offset for navbar
            }, 500);
        }
    });
    
    // ============================================
    // BUTTON TRACKING (for analytics)
    // ============================================
    
    /**
     * Log button clicks for debugging/analytics
     * In production, this could send data to an analytics service
     */
    $(".btn").on("click", function() {
        const buttonText = $(this).text().trim();
        console.log("Button clicked:", buttonText);
        
        // Optional: Track with analytics
        // if (typeof gtag !== 'undefined') {
        //     gtag('event', 'button_click', { 'button_text': buttonText });
        // }
    });
    
    // ============================================
    // NAVBAR SCROLL EFFECT
    // ============================================
    
    /**
     * Add shadow to navbar when page is scrolled
     * Creates a subtle visual separation from content
     */
    $(window).on('scroll', function() {
        const navbar = $('.navbar');
        
        if ($(window).scrollTop() > 10) {
            navbar.addClass('shadow-sm');
        } else {
            navbar.removeClass('shadow-sm');
        }
    });
});
