---
title: Random Quotes for Hugo
revision_date: 2022-09-18
hide:
  - navigation
#  - toc
#  - footer
tags:
  - hugo
---

I wanted to add random quotes to a static Hugo site and I couldn't find any widgets, so I wrote one. I thought this would be an excellent way to learn more about extending Hugo, and it was.

> :point_right: &nbsp; See [my working example](https://random-quote.fortc.com) and [GitHub repository](https://github.com/dfinster/hugo-random-quotes).

I wanted a shortcode and a page partial widget that used the same code in a DRY approach, but Hugo passes the parameters differently to these types. In the end it was cleaner to repeat the logic in both places, and you have the option to use only one format if you don't need the other one. I may revisit this later if I find a better solution.

## How to add random quotes to your Hugo template

Here's how to add it to your Hugo site.

 1. Add [the shortcode](https://github.com/dfinster/hugo-random-quotes/blob/main/layouts/shortcodes/quote.html) to `/layouts/shortcodes` in your template.
 1. Add the [page partial](https://github.com/dfinster/hugo-random-quotes/blob/main/layouts/partials/quote.html) to `/layouts/partials`.
 1. Add `.quote_heading`, `.quote_text`, and `.quote_source` from the [example stylesheet](https://github.com/dfinster/hugo-random-quotes/blob/main/assets/scss/custom.scss) to your theme's custom style.
 1. Add a `quotes.csv` file to the root of your Hugo project. Here's [a link to mine](https://github.com/dfinster/hugo-random-quotes/blob/main/quotes.csv).

#### About the CSV file

Although it's `CSV`, I used a pipe as the field delimiter because quotations tend to have commas embedded, along with other embedded quote marks. I punted while coding the minimum viable example and haven't fixed it yet.

Records have two fields, like this:

    "This is the 'first' quote."|"— Someone"
    "This is the “second” quote."|"— Someone Else"

Fields are delimited with double-quotes. Due to how Hugo and JavaScript pass the data, it's difficult to properly escape double-quotes if you need to express them. Instead, you should use single quotes, or use Unicode curly-quotes like the “second” quote above.

## How to use the shortcode

Add this shortcode to any Hugo page.

```txt
{{% quote [style] [heading] %}}
```

`style` is an integer.

* Style `1` has no formatting or CSS. It displays a random quote and the source, separated by a single space. Style 1 does not support a heading.
* Style `2` is the default if you omit the parameter. It shows an optional heading, the text, and the source with CSS selectors you can style.

`heading` is an optional string to display above the quote.

## Shortcode examples

Here is a formatted quote in style 2 with no heading.

```txt
{{% quote %}}
```

Here is an unformatted quote.

```txt
{{% quote 1 *%}}
```

Here is a formatted quote with a heading.

```txt
{{% quote 2 "Quote of the Day" %}}
```

## How to use the page partial

The page partial version requires extra fields in the page's front-matter:

```yaml
quote: 
  style: 2
  display: true
  heading: "Quote of the Day"
```

`style` is an integer. Valid values are `1` and `2`.

* Style `1` has no formatting or CSS. It displays a random quote and the source, separated by a single space. Style 1 does not support a heading.
* Style `2` is the default if you omit the parameter. It shows an optional heading, the text, and the source with CSS selectors you can style.

`display` is boolean.

* `true` = display
* `false` = hide

`heading` is an optional string to display above the quote.

## Page partial example

To call the page partial, add this to a page.

```txt
{{ partial "quote.html" . }}
```

## Limitations

You cannot add random quotes more than one place on a single page. This is a possible area for improvement.
