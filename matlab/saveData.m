function saveData(file)
%Extract and save data from Cx.mat files.
%Saved data: Seesaw and optimal strats QSW.

loadNPAData;
data = load(file);

pad_begin_id = data.v0(1)/data.stepsize - 1;    
    
v0 = 0:data.stepsize:2;
v1 = 2 - v0;
ratio = v0./v1;

if strcmp(file, 'C3.mat')

    classical_qsw = (ratio <= 1).*(1/12*(2*v0 + 7*v1)) + (ratio > 1).*(1/12*(9*v0));
    
    %Pad seesaw qsw with that of classical strategies.
    qsw = [classical_qsw(1:pad_begin_id), data.QSW, classical_qsw(pad_begin_id + 1 + length(data.QSW): end)];
    
    [fid, msg] = fopen('data/classical_C3_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', classical_qsw);
    fclose(fid);
    
    [fid, msg] = fopen('data/seeesaw_C3_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', qsw);
    fclose(fid);
    
    [fid, msg] = fopen('data/graphState_C3_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', (v0 + v1)/2);
    fclose(fid);
    
elseif strcmp(file, 'C5.mat')

    classical_qsw = (ratio <= 1/3).*(1/30*(8*v0 + 17*v1)) + (ratio > 1/3 & ratio <= 1).*(1/30*(6*v0 + 19*v1)) + (ratio > 1).*(1/30*(25*v0));
    
    %Pad seesaw qsw with that of classical strategies.
    qsw = [classical_qsw(1:pad_begin_id), data.QSW, classical_qsw(pad_begin_id + 1 + length(data.QSW): end)];     
            
    [fid, msg] = fopen('data/classical_C5_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', classical_qsw);
    fclose(fid);
    
    [fid, msg] = fopen('data/seeesaw_C5_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', qsw);
    fclose(fid);
    
    %GraphState not equilibrium everywhere
    v0 = 2/3:data.stepsize:2;
    v1 = 2 - v0;
     
    [fid, msg] = fopen('data/graphState_C5_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', (v0 + v1)/2);
    fclose(fid);
    

elseif strcmp(file, 'C5sym.mat')
    
    classical_qsw = (ratio <= 1/3).*(1/30*(4*v0 + 11*v1)) + (ratio > 1/3 & ratio <= 1).*(1/30*(5*v0 + 20*v1)) + (ratio > 1).*(1/30*(25*v0));

        %Pad seesaw qsw with that of classical strategies.
    qsw = [classical_qsw(1:pad_begin_id), data.QSW, classical_qsw(pad_begin_id + 1 + length(data.QSW): end)]; 
    
    [fid, msg] = fopen('data/classical_C5Ssym_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', classical_qsw);
    fclose(fid);
    
    [fid, msg] = fopen('data/seeesaw_C5Sym_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', qsw);
    fclose(fid);
    
    v0 = 1/2:data.stepsize:2;
    v1 = 2 - v0;
    
    [fid, msg] = fopen('data/graphState_C5Sym_0_2', 'wt');
    assert(fid>=3, msg);
    fprintf(fid, '%d\n', (v0 + v1)/2);
    fclose(fid);
    

    
end

end

