# Mobile Compatibility Test Plan

## Overview
This test plan covers mobile responsive design for DessertAble on modern phones (375px-430px width range).

## Test Devices Recommended
- **iPhone SE** (375px wide) - Smallest target device
- **iPhone 12/13/14** (390px wide) - Most common
- **iPhone 14 Pro Max** (430px wide) - Largest target device
- **Android equivalents** (Samsung Galaxy S21, Pixel 6, etc.)

## How to Test

### Option 1: Real Device Testing
1. Open your phone's browser (Safari on iOS, Chrome on Android)
2. Navigate to your DessertAble URL
3. Follow the test cases below

### Option 2: Browser Developer Tools
1. Open Chrome/Firefox/Safari
2. Press F12 or Cmd+Option+I (Mac) to open DevTools
3. Click the device toolbar icon (phone/tablet icon)
4. Select device from dropdown or set custom width:
   - iPhone SE: 375px
   - iPhone 12 Pro: 390px
   - iPhone 14 Pro Max: 430px
5. Test in both portrait and landscape orientations

---

## Test Cases

### 1. Navigation & Hamburger Menu

#### Test 1.1: Hamburger Menu Visibility
- [ ] **Viewport**: 375px-480px width
- [ ] **Expected**: Hamburger menu (three horizontal lines) visible in top-right
- [ ] **Expected**: Desktop navigation links hidden
- [ ] **Expected**: DessertAble logo visible and tappable

#### Test 1.2: Hamburger Menu Interaction
- [ ] Tap hamburger menu button
- [ ] **Expected**: Menu slides in from right side
- [ ] **Expected**: Dark overlay appears behind menu
- [ ] **Expected**: Hamburger icon animates to "X" shape
- [ ] **Expected**: Page body scroll is disabled when menu is open

#### Test 1.3: Menu Content (Logged Out)
- [ ] Open hamburger menu while logged out
- [ ] **Expected**: "Login" link visible
- [ ] **Expected**: "Sign Up" link visible
- [ ] **Expected**: Links are large enough to tap easily (44px minimum height)

#### Test 1.4: Menu Content (Logged In)
- [ ] Log in to the app
- [ ] Open hamburger menu
- [ ] **Expected**: "Favorites" link visible
- [ ] **Expected**: "History" link visible
- [ ] **Expected**: Username displayed in blue
- [ ] **Expected**: "Logout" link visible

#### Test 1.5: Menu Closing
- [ ] Open menu and tap the dark overlay
- [ ] **Expected**: Menu closes
- [ ] Open menu and tap any navigation link
- [ ] **Expected**: Menu closes and navigates to that page
- [ ] Open menu and tap hamburger button again
- [ ] **Expected**: Menu closes

---

### 2. Home Page (Search Page)

#### Test 2.1: Layout & Spacing
- [ ] Navigate to home page
- [ ] **Viewport**: 375px width (iPhone SE)
- [ ] **Expected**: Page heading "Find dessert near you" is readable (not cut off)
- [ ] **Expected**: Heading size is proportional (~2rem, not too large)
- [ ] **Expected**: Search input field is full width
- [ ] **Expected**: Comfortable margins around content (not edge-to-edge)

#### Test 2.2: Form Input
- [ ] Tap on the address input field
- [ ] **Expected**: Input expands properly and is easy to type in
- [ ] **Expected**: Placeholder text is visible: "Enter your address"
- [ ] **Expected**: On-screen keyboard doesn't obscure the input
- [ ] **Expected**: Border animation works smoothly on focus

#### Test 2.3: Search Button
- [ ] Check the "Search" button
- [ ] **Expected**: Button is full width
- [ ] **Expected**: Button text is clearly readable
- [ ] **Expected**: Button is large enough to tap comfortably (minimum 44px height)
- [ ] **Expected**: Button has appropriate padding and doesn't look cramped

---

### 3. Search Results Page

#### Test 3.1: Results Layout
- [ ] Perform a search and view results
- [ ] **Viewport**: 375px-430px
- [ ] **Expected**: Restaurant cards stack vertically (1 column)
- [ ] **Expected**: Carousel navigation arrows (< >) are hidden on mobile
- [ ] **Expected**: All result cards are visible without needing to navigate

#### Test 3.2: Restaurant Card Content
- [ ] Scroll through results
- [ ] **Expected**: Restaurant name is readable and not cut off
- [ ] **Expected**: Sprite images are appropriately sized (not too large)
- [ ] **Expected**: Rating, cuisine type, and hours are clearly visible
- [ ] **Expected**: AI description text is legible
- [ ] **Expected**: Drive time with car emoji is visible
- [ ] **Expected**: Card padding is comfortable (not cramped)

#### Test 3.3: Card Interaction
- [ ] Tap a restaurant name
- [ ] **Expected**: Opens Google Maps in new tab
- [ ] Test OPEN/CLOSED badge
- [ ] **Expected**: Badge is clearly visible and readable

#### Test 3.4: Favorite Button (Logged In Only)
- [ ] Log in if not already
- [ ] View search results
- [ ] **Expected**: Heart icon (♡) visible in top-right of each card
- [ ] **Expected**: Heart icon is large enough to tap easily
- [ ] Tap heart icon
- [ ] **Expected**: Heart fills (♥) and turns blue
- [ ] **Expected**: Visual feedback (slight scale animation)
- [ ] Tap filled heart again
- [ ] **Expected**: Heart unfills back to outline

#### Test 3.5: "New Search" Link
- [ ] Scroll to bottom of results page
- [ ] **Expected**: "← New search" link is visible and centered
- [ ] Tap the link
- [ ] **Expected**: Returns to home page

---

### 4. Login Page

#### Test 4.1: Layout
- [ ] Navigate to login page
- [ ] **Viewport**: 375px width
- [ ] **Expected**: "Log in" heading is centered and readable
- [ ] **Expected**: Form is centered with appropriate margins
- [ ] **Expected**: Page doesn't feel cramped

#### Test 4.2: Form Inputs
- [ ] Tap username field
- [ ] **Expected**: Input is large enough and easy to type in
- [ ] **Expected**: Focus border animation works
- [ ] Tap password field
- [ ] **Expected**: Password is masked properly
- [ ] **Expected**: Input expands correctly on focus

#### Test 4.3: Remember Me Checkbox
- [ ] Find "Remember me" checkbox
- [ ] **Expected**: Checkbox is at least 20px × 20px (easy to tap)
- [ ] **Expected**: Label text is next to checkbox and readable

#### Test 4.4: Login Button
- [ ] Check the "Log in" button
- [ ] **Expected**: Button is full width
- [ ] **Expected**: Button is large enough to tap comfortably
- [ ] **Expected**: Text is centered and readable

#### Test 4.5: Sign Up Link
- [ ] Scroll to "Don't have an account? Sign up" link
- [ ] **Expected**: Text is readable and link is highlighted
- [ ] Tap the "Sign up" link
- [ ] **Expected**: Navigates to registration page

---

### 5. Registration Page

#### Test 5.1: Layout
- [ ] Navigate to registration page
- [ ] **Viewport**: 375px width
- [ ] **Expected**: "Create account" heading is centered and readable
- [ ] **Expected**: Form is centered with appropriate margins

#### Test 5.2: Form Inputs
- [ ] Test all three input fields (username, password, confirm password)
- [ ] **Expected**: All inputs are properly sized and easy to type in
- [ ] **Expected**: Placeholder text is visible
- [ ] **Expected**: Password fields mask input properly

#### Test 5.3: Create Account Button
- [ ] Check the "Create account" button
- [ ] **Expected**: Button is full width and easy to tap
- [ ] **Expected**: Text is centered and readable

#### Test 5.4: Login Link
- [ ] Scroll to "Already have an account? Log in" link
- [ ] **Expected**: Text is readable and link is highlighted
- [ ] Tap the "Log in" link
- [ ] **Expected**: Navigates back to login page

---

### 6. Cross-Page Tests

#### Test 6.1: Navigation Between Pages
- [ ] Navigate through all pages using the hamburger menu
- [ ] **Expected**: Menu closes after tapping each link
- [ ] **Expected**: New page loads correctly
- [ ] **Expected**: No horizontal scrolling on any page

#### Test 6.2: Flash Messages
- [ ] Trigger a flash message (e.g., failed login)
- [ ] **Expected**: Alert message is readable on mobile
- [ ] **Expected**: Alert doesn't overflow screen width
- [ ] **Expected**: Alert text size is appropriate

#### Test 6.3: Footer
- [ ] Scroll to bottom on any page
- [ ] **Expected**: Footer text "© 2026 DessertAble" is centered
- [ ] **Expected**: Footer doesn't overlap with content
- [ ] **Expected**: Footer text is readable

---

### 7. Touch Interactions

#### Test 7.1: Touch Target Sizes
- [ ] Test all buttons and links across all pages
- [ ] **Expected**: All interactive elements are at least 44px tall (iOS guideline)
- [ ] **Expected**: Adequate spacing between tappable elements

#### Test 7.2: Touch Feedback
- [ ] Tap various links and buttons
- [ ] **Expected**: Visual feedback on tap (no hover states on mobile)
- [ ] **Expected**: No accidental double-taps required

---

### 8. Landscape Orientation

#### Test 8.1: Landscape Layout
- [ ] Rotate device to landscape mode
- [ ] Test all pages in landscape
- [ ] **Expected**: Content is still readable
- [ ] **Expected**: No awkward spacing or layout issues
- [ ] **Expected**: Hamburger menu still works in landscape

---

### 9. Tablet Compatibility (Bonus)

#### Test 9.1: iPad/Tablet View (768px)
- [ ] **Viewport**: 768px width
- [ ] Navigate to results page
- [ ] **Expected**: Restaurant cards display in 2 columns
- [ ] **Expected**: Desktop navigation visible (no hamburger menu)

---

## Success Criteria

### Must Pass (Critical)
- ✅ Hamburger menu works on phones (< 480px)
- ✅ All pages are readable without horizontal scrolling
- ✅ All forms are usable on mobile
- ✅ Touch targets are at least 44px tall
- ✅ Search and login/register flows work end-to-end

### Should Pass (Important)
- ✅ Restaurant cards display well on mobile
- ✅ Navigation menu closes properly
- ✅ Text sizes are appropriate (not too small)
- ✅ No content is cut off or hidden

### Nice to Have
- ✅ Smooth animations and transitions
- ✅ Landscape orientation works well
- ✅ Tablet view (768px) displays properly

---

## Common Issues to Watch For

1. **Horizontal Scrolling**: Content should never require horizontal scrolling
2. **Text Too Small**: Minimum body text should be 16px on mobile
3. **Buttons Too Small**: Touch targets smaller than 44px are hard to tap
4. **Content Overlap**: Menu, modals, or overlays covering important content
5. **Form Issues**: Inputs too small, keyboard obscuring submit button
6. **Image Scaling**: Sprites or images too large or distorted

---

## Reporting Issues

If you find any issues during testing, note:
- **Device/Viewport**: Exact width (e.g., "iPhone SE, 375px")
- **Page**: Which page the issue occurs on
- **Issue**: What's wrong (with screenshot if possible)
- **Expected**: What should happen instead

---

## Testing Complete

Once all test cases pass, your mobile compatibility implementation is complete! 🎉

**Note**: Modern phones primarily range from 375px (iPhone SE) to 430px (iPhone 14 Pro Max). The design prioritizes this range while maintaining compatibility with tablets (768px+) using a 2-column layout.
