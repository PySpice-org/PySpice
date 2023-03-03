// #################################################################################################
//
// Gulp Task Manager settings
//
// Documentation https://gulpjs.com
// https://www.liquidlight.co.uk/blog/how-do-i-update-to-gulp-4
//
// #################################################################################################

// #################################################################################################
//
// Copyright (c) 2019 Fabrice Salvaire
//
// Copyright (c) 2013, Divio AG
// Licensed under BSD
// http://github.com/aldryn/aldryn-boilerplate-bootstrap3
//
// #################################################################################################

// #################################################################################################
// IMPORTS

// https://www.npmjs.com/package/autoprefixer
// PostCSS plugin to parse CSS and add vendor prefixes to CSS rules using values from Can I Use.
// It is recommended by Google and used in Twitter.
var autoprefixer = require('autoprefixer');
var eslint = require('gulp-eslint');
var fs = require('fs');
var gulp = require('gulp');
var gulpif = require('gulp-if');
var gutil = require('gulp-util');
var header = require('gulp-header');
var iconfont = require('gulp-iconfont');
var iconfont_css = require('gulp-iconfont-css');
// https://www.npmjs.com/package/gulp-clean-css
// https://github.com/jakubpawlowicz/clean-css
var minify_css = require('gulp-clean-css');
var plumber = require('gulp-plumber');
var postcss = require('gulp-postcss');
var gulp_sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
// var webpack = require('webpack');
var browser_sync = require('browser-sync').create();

var argv = require('minimist')(process.argv.slice(2));

// #################################################################################################
// SETTINGS

var options = {
    debug: argv.debug
};

var PROJECT_ROOT = __dirname;

var PROJECT_PATH = {
    bower: PROJECT_ROOT + '/static/vendor',
    css: PROJECT_ROOT + '/static/css',
    fonts: PROJECT_ROOT + '/static/fonts', // Doesn't exists !!!
    html: PROJECT_ROOT + '/templates',
    icons: PROJECT_ROOT + '/private/icons', // Doesn't exists !!!
    images: PROJECT_ROOT + '/static/img',
    js: PROJECT_ROOT + '/static/js',
    sass: PROJECT_ROOT + '/scss',
};

var PROJECT_PATTERNS = {
    html: [
        PROJECT_PATH.html + '/**/*.{html}'
    ],
    images: [
        PROJECT_PATH.images + '/**/*',
    ],
    js: [
        'gulpfile.js',
        PROJECT_PATH.js + '/**/*.js',
        // exclude from linting
        '!' + PROJECT_PATH.js + '/*.min.js',
        '!' + PROJECT_PATH.js + '/**/*.min.js',
    ],
    sass: [
        PROJECT_PATH.sass + '/**/*.{scss,sass}'
    ]
};

var DEFAULT_PORT = 8000;
var PORT = parseInt(process.env.PORT, 10) || DEFAULT_PORT;
var DEBUG = argv.debug;

// #################################################################################################
// TASKS

// SASS Task
function sass_task(cb) {
    // sourcemaps can be activated through `gulp sass --debug´
    gulp
        .src(PROJECT_PATTERNS.sass)
        .pipe(gulpif(options.debug, sourcemaps.init()))
        .pipe(gulp_sass())
        .on('error', function(error) {
            gutil.log(gutil.colors.red('Error (' + error.plugin + '): ' + error.messageFormatted));
        })
        .pipe(
            postcss([
                autoprefixer({
                    cascade: false
                })
            ])
        )
        .pipe(
            minify_css({
                rebase: false
            })
        )
        .pipe(header('/* This file was generated automatically on server side on ' + new Date().toISOString() +
                     '. All changes would be lost. */ \n\n'))
        .pipe(gulpif(options.debug, sourcemaps.write()))
        .pipe(gulp.dest(PROJECT_PATH.css))
        .pipe(browser_sync.reload({
            stream: true,
        }));
    cb();
}

// Icons Task
function icons_task(cb) {
    // /private/icons Doesn't exists !!!
    gulp
        .src(PROJECT_PATH.icons + '/**/*.svg')
        .pipe(
            iconfont_css({
                fontName: 'iconfont',
                appendUnicode: true,
                formats: ['ttf', 'eot', 'woff', 'svg'],
                fontPath: 'static/fonts/',
                path: PROJECT_PATH.sass + '/libs/_iconfont.scss',
                targetPath: '../../../scss/layout/_iconography.scss'
            })
        )
        .pipe(
            iconfont({
                fontName: 'iconfont',
                normalize: true
            })
        )
        .on('glyphs', function(glyphs, opts) {
            gutil.log.bind(glyphs, opts);
        })
        .pipe(gulp.dest(PROJECT_PATH.fonts));
    cb();
}

// Lint Task
function lint_javascript_task(cb) {
    // http://eslint.org
    gulp
        .src(PROJECT_PATTERNS.js)
        .pipe(gulpif(!process.env.CI, plumber()))
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failAfterError())
        .pipe(gulpif(!process.env.CI, plumber.stop()));
    cb();
}

// Django Dev Server Task
function runserver_task(cb) {
    var proc = exec('python manage.py runserver');
    cb();
}

// Browser Sync Task
// gulp.task('browserSync', ['runserver'], function() {});
function browser_sync_task(cb) {
    browser_sync.init({
        notify: false,
        port: DEFAULT_PORT,
        proxy: 'localhost:' + DEFAULT_PORT,
    });
    cb();
}

// Watch Task
function watch_task(cb) {
    gulp.watch(PROJECT_PATTERNS.html, browser_sync.reload);
    gulp.watch(PROJECT_PATTERNS.sass, gulp.series(sass_task));
    // gulp.watch(PROJECT_PATTERNS.js, lint_javascript_task);
    cb();
}

// #################################################################################################

exports.sass = sass_task;
exports.build = gulp.series(sass_task);
exports.default = gulp.series(browser_sync_task, sass_task, watch_task);
exports.lint = gulp.series(lint_javascript_task);

// #################################################################################################

// Checks project deployment
// @param {String} id - task name
// @returns {Object} - task which finished
// function task (id) {
//     return require('./tools/tasks/' + id)(gulp, {
//         PROJECT_ROOT: PROJECT_ROOT,
//         PROJECT_PATH: PROJECT_PATH,
//         PROJECT_PATTERNS: PROJECT_PATTERNS,
//         DEBUG: DEBUG,
//         PORT: PORT
//     });
// }
//
// gulp.task('sass', task('sass'));
