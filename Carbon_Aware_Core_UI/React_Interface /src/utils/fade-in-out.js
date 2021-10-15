const fade_in_out = () => {
    const contentEles = document.getElementsByClassName("fade-in")
    console.log(contentEles)
    
    const appearOptions = {
        threshold: 1,
        rootMargin: "-15% 0px 0px 0px"
    }

    const appearOnScroll = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("appear")
            } else {
                entry.target.classList.remove("appear")
            }
        })
    }, appearOptions)

    Array.from(contentEles).forEach((ele) => {
        appearOnScroll.observe(ele)
    })
}

export default fade_in_out