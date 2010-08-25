/*
 * Toonloop
 *
 * Copyright 2010 Alexandre Quessy
 * <alexandre@quessy.net>
 * http://www.toonloop.com
 *
 * Toonloop is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Toonloop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the gnu general public license
 * along with Toonloop.  If not, see <http://www.gnu.org/licenses/>.
 */
#ifndef __APPLICATION_H__
#define __APPLICATION_H__

#include <boost/program_options.hpp>
#include <boost/scoped_ptr.hpp>

#include "clip.h"
#include "configuration.h"
#include "gui.h"
#include "midi.h"
#include "oscinterface.h"
#include "pipeline.h"
#include "moviesaver.h"

// FIXME:2010-08-17:aalex:We should allow more than 10 clips
#define MAX_CLIPS 10

namespace po = boost::program_options;

bool make_sure_directory_exists(std::string directory);;

class Application 
{
    public:
        void run(int argc, char *argv[]);
        void quit();
        Gui *get_gui();
        Pipeline *get_pipeline();
        MidiInput *get_midi_input();
        Configuration *get_configuration();
        MovieSaver *get_movie_saver();
        static Application& get_instance();
        Clip* get_current_clip();
        bool save_current_clip();
        int get_current_clip_number();
        void set_current_clip_number(int clipnumber);
        void on_pedal_down();

    private:
        Application();
        ~Application();
        void update_project_home_for_each_clip();
        bool setup_project_home(std::string project_home);
        boost::scoped_ptr<Gui> gui_;
        boost::scoped_ptr<MidiInput> midi_input_;
        boost::scoped_ptr<OscInterface> osc_;
        boost::scoped_ptr<Pipeline> pipeline_;
        boost::scoped_ptr<Configuration> config_;
        boost::scoped_ptr<MovieSaver> movie_saver_;
        int selected_clip_;
        // Aug 25 2010:tmatth:TODO:use shared_ptr, not raw pointers for clips_
        typedef std::tr1::unordered_map<int, Clip*>::iterator ClipIterator;
        std::tr1::unordered_map<int, Clip*> clips_;
};

#endif // __APPLICATION_H__
